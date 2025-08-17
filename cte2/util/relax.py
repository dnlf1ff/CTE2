from ase.constraints import FixSymmetry, FixAtoms
from ase.filters import UnitCellFilter, FrechetCellFilter
from ase.optimize import LBFGS, FIRE, FIRE2
import numpy as np
from ase import Atoms

OPT_DICT = {'fire': FIRE, 'fire2':FIRE2,'lbfgs': LBFGS}
FILTER_DICT = {'frechet': FrechetCellFilter, 'unitcell': UnitCellFilter}


"""
modified based on Jaesun Kim's code
"""

class AseAtomRelax:
    def __init__(
        self,
        calc,
        optimizer,
        cell_filter=None,
        mask=None,
        fix_atom=False,
        fix_symm=False,
        fmax=0.00001,
        steps=1000,
        logfile='ase_relaxer.log'
    ):
        self.calc = calc
        self.optimizer = optimizer
        self.cell_filter = cell_filter
        self.mask = mask
        self.fix_atom = fix_atom
        self.fix_symm = fix_symm
        self.fmax = fmax
        self.steps = steps
        self.logfile = logfile

    def _get_atoms(self, atoms_0):
        atoms = atoms_0.copy()
        if self.fix_symm:
            atoms.set_constraint(FixSymmetry(atoms, symprec=1e-5))

        if self.fix_atom:
            z =atoms.positions[:,2].copy()
            indices = [atom.index for atom in atoms if atom.position[2] < np.percentile(z,62) and atom.position[2]>np.percentile(z,38)]
            atoms.set_constraint(FixAtoms(indices=indices))
            atoms.set_pbc([True, True, True])
        return atoms

    def update_atoms(self, atoms_0):
        atoms = self._get_atoms(atoms_0)
        atoms.calc = self.calc

        try:
            atoms.info['e_fr_energy'] = atoms.get_potential_energy(force_consistent=True)
        except:
            atoms.info['e_fr_energy'] = atoms.get_potential_energy()
        atoms.info['e_0_energy'] = atoms.get_potential_energy()
        atoms.info['force'] = atoms.get_forces()
        conv = check_atoms_conv(atoms.get_forces())
        atoms.info['conv'] = conv
        atoms.info['stress'] = atoms.get_stress()
        atoms.info['stress_voigt'] = atoms.get_stress(voigt=True)
        return atoms

    def relax_atoms(self, atoms_0):
        atoms = self._get_atoms(atoms_0)
        atoms.calc = self.calc

        if self.cell_filter is not None:
            if self.mask is not None:
                cell_filter = self.cell_filter(atoms, mask=self.mask)
            else:
                cell_filter = self.cell_filter(atoms)
            optimizer = self.optimizer(cell_filter, logfile=self.logfile)
        else:
            optimizer = self.optimizer(atoms, logfile=self.logfile)
        conv = optimizer.run(fmax=self.fmax, steps=self.steps)
        return atoms

def aar_from_config(config, calc, opt_type, logfile=None):
    arr_args = config['opt'][opt_type].copy()

    try:
        opt = OPT_DICT[arr_args['optimizer'].lower()]

    except Exception as e:
        print(f'error {e} occured while finding optimizer')
        opt = OPT_DICT['fire']
        print(f'will use ase.optimize.FIRE')

    try:
        cell_filter = FILTER_DICT[arr_args.get('cell_filter', None)]

    except Exception as e:
        cell_filter = None

    if logfile is not None:
        arr_args['logfile'] = logfile
    else:
        arr_args['logfile'] = f"{config['cwd']}/{opt}.log"

    arr_args['calc'] = calc
    arr_args['optimizer'] = opt
    arr_args['cell_filter'] = cell_filter

    return AseAtomRelax(**arr_args)

def check_atoms_conv(forces: np.ndarray) -> bool:
    conv = True
    for i in range(forces.shape[-1]):
        if np.any(forces[:,i]) < 0:
            conv = False
    return conv



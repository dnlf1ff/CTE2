from ase.constraints import FixSymmetry, FixAtoms
from ase.filters import UnitCellFilter, FrechetCellFilter
from ase.optimize import LBFGS, FIRE, FIRE2
import numpy as np
from ase import Atoms

OPT_DCT = {'fire': FIRE, 'fire2':FIRE2,'lbfgs': LBFGS}
FILTER_DCT = {'frechet': FrechetCellFilter, 'unitcell': UnitCellFilter}


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
        fix_symm=True,
        fmax=0.00001,
        steps=10000,
        logfile='ase_relaxer.log'
    ):
        self.calc = calc
        self.optimizer = optimizer
        self.cell_filter = cell_filter
        self.mask = mask
        self.fix_symm = fix_symm
        self.fmax = fmax
        self.steps = steps
        self.logfile = logfile

    def update_atoms(self, atoms):
        atoms = atoms.copy()
        atoms.calc = self.calc

        atoms.info['e_fr_energy'] = atoms.get_potential_energy(force_consistent=True)
        atoms.info['e_0_energy'] = atoms.get_potential_energy()
        atoms.info['force'] = atoms.get_forces()
        conv = check_atoms_conv(atoms.get_forces())
        atoms.info['conv'] = conv
        return atoms

    def relax_atoms(self, atoms):
        atoms = atoms.copy()
        atoms.calc = self.calc
        cell_filter = self.cell_filter(atoms, mask=self.mask)
        optimizer = self.optimizer(cell_filter, logfile=self.logfile)
        conv = optimizer.run(fmax=self.fmax, steps=self.steps)
        return atoms

def get_aar(config, calc, opt_type='unitcell', cell_filter=None, logfile='ase_relax.log'):
    arr_args = config['opt'][opt_type].copy()

    opt = OPT_DICT[arr_args['optimizer'].lower()]
    cell_filter = FILTER_DICT[arr_args['cell_filter']]

    arr_args['calc'] = calc
    arr_args['optimizer'] = opt
    arr_args['cell_filter'] = cell_filter
    arr_args['logfile'] = logfile
    return AseAtomRelax(**arr_args)

def check_atoms_conv(forces: np.ndarray) -> bool:
    conv = True
    for i in range(forces.shape[-1]):
        if np.any(forces[:,i]) < 0:
            conv = False
    return conv



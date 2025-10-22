from ase.constraints import FixSymmetry
from ase.filters import UnitCellFilter, FrechetCellFilter
from ase.optimize import LBFGS, FIRE, FIRE2
import numpy as np

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
        fmax=0.000001,
        steps=5000,
        logfile='ase_relaxer.log',
        constant_volume = False
    ):
        self.calc = calc
        self.optimizer = optimizer
        self.cell_filter = cell_filter
        self.mask = mask
        self.fix_symm = fix_symm
        self.fmax = fmax
        self.steps = steps
        self.logfile = logfile
        if self.mask == [0, 0, 0, 0, 0, 0]:
            constant_volume = True
        self.constant_volume = constant_volume

    def update_atoms(self, atoms):
        atoms = atoms.copy()
        atoms.calc = self.calc

        atoms.info['e_fr_energy'] = atoms.get_potential_energy(force_consistent=True)
        atoms.info['e_0_energy'] = atoms.get_potential_energy()
        atoms.info['force'] = atoms.get_forces()
        atoms.info['position'] = atoms.get_positions()
        atoms.info['formula'] = atoms.get_chemical_formula(empirical=True)
        atoms.info['symbol'] = atoms.get_chemical_symbols()
        atoms.info['stress'] = atoms.get_stress(voigt=False)
        atoms.info['stress_voigt'] = atoms.get_stress()
        atoms.info['volume'] = atoms.get_volume()
        atoms.info['a'] = atoms.cell.lengths()[0]
        atoms.info['b'] = atoms.cell.lengths()[1]
        atoms.info['c'] = atoms.cell.lengths()[2]
        atoms.info['alpha'] = atoms.cell.angles()[0]
        atoms.info['beta'] = atoms.cell.angles()[1]
        atoms.info['gamma'] = atoms.cell.angles()[2]

        force_conv = check_atoms_conv(atoms.get_forces())
        atoms.info['force_conv'] = force_conv
        return atoms

    def relax_atoms(self, atoms):
        atoms = atoms.copy()
        if self.fix_symm:
            atoms.set_constraint(FixSymmetry(atoms, symprec=1e-05))

        atoms.calc = self.calc
        if self.constant_volume:
            cell_filter = self.cell_filter(atoms, constant_volume = self.constant_volume, mask=self.mask)
        else:
            cell_filter = self.cell_filter(atoms, mask=self.mask)
        optimizer = self.optimizer(cell_filter, logfile=self.logfile)
        optimizer.run(fmax=self.fmax, steps=self.steps)
        opt_steps = optimizer.get_number_of_steps()
        atoms.info['opt_steps'] = opt_steps
        opt_fin = True
        if opt_steps >= self.steps:
            opt_fin = False
        atoms.info['opt_conv'] = opt_fin
        atoms.info['opt'] = 'post'
        return atoms

    def redo(self, atoms):
        atoms = atoms.copy()
        if self.fix_symm:
            atoms.set_constraint(FixSymmetry(atoms, symprec=1e-05))

        atoms.calc = self.calc
        if self.constant_volume:
            cell_filter = self.cell_filter(atoms, constant_volume = self.constant_volume, mask=self.mask)
        else:
            cell_filter = self.cell_filter(atoms, mask=self.mask)
        optimizer = self.optimizer(cell_filter, logfile=self.logfile)
        optimizer.run(fmax=0.00001, steps=20000)
        opt_steps = optimizer.get_number_of_steps()
        atoms.info['opt_steps'] = opt_steps
        opt_fin = True
        if opt_steps >= self.steps:
            opt_fin = False
        atoms.info['opt_conv'] = opt_fin
        atoms.info['opt'] = 'post'
        return atoms

def get_ase_relaxer(config, calc, opt_type='unitcell', cell_filter=None, logfile='ase_relax.log'):
    arr_args = config['opt'][opt_type].copy()

    opt = OPT_DCT[arr_args['optimizer'].lower()]
    cell_filter = FILTER_DCT[arr_args['cell_filter']]

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



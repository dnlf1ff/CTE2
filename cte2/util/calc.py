import numpy as np
from tqdm import tqdm
from sevenn.calculator import SevenNetCalculator
from ase.calculators.singlepoint import SinglePointCalculator

"""
modified based on Jaesun Kim's code
"""

def get_calc(config):
    conf = config['calculator']
    model = conf['model_path']
    calc_type = conf['calc_type']
    calc_args = conf['calc_args']

    print(f"[{calc_type}]")
    print(f"[{calc_type}] potential path: {model_path}")
    print(f"[{calc_type}] calc_kwrgs: {calc_args}")
    
    calc = SevenNetCalculator(model = model_path, **calc_args)
    return calc


def single_point_calculate(atoms, calc=None):
    if calc is not None:
        atoms.calc = calc
    energy = atoms.get_potential_energy()
    forces = atoms.get_forces()
    stress = atoms.get_stress()

    calc_results = {"energy": energy, "forces": forces, "stress": stress}
    calculator = SinglePointCalculator(atoms, **calc_results)
    new_atoms = calculator.get_atoms()

    return new_atoms


def single_point_calculate_list(atoms_list, calc, desc=None):
    calculated = []
    for atoms in tqdm(atoms_list, desc=desc, leave=False):
        calculated.append(single_point_calculate(atoms, calc))

    return calculated

import numpy as np
from tqdm import tqdm
from sevenn.calculator import SevenNetCalculator
from ase.calculators.singlepoint import SinglePointCalculator

"""
modified based on Jaesun Kim's code
"""

def calc_from_py(config):
    import importlib.util
    from pathlib import Path

    file_path = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(f'load_calc', f'{file_path}/loader.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    calc = module.load_calc(config)
    return calc

def calc_from_config(config):
    calc_conf = config['calculator'].copy()
    calc_type = calc_conf['calc_type'].lower()

    if calc_type in ['sevennet-mf', '7net-mf']:
        calc_kwargs = {'model': calc_conf['calc_args']['model'],
                   'modal': calc_conf['calc_args']['modal'],
                   'device': calc_conf['calc_args']['device']}
        return SevenNetCalculator(**calc_kwargs)

    elif calc_type in ['sevennet', '7net']:
        calc_kwargs = {'model': calc_conf['calc_args']['model'],
                   'device': calc_conf['calc_args']['device']}
        return SevenNetCalculator(**calc_kwargs)
    
    elif calc_type in ['dft', 'vasp']:
        return None

    else:
        return calc_from_py(config)


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

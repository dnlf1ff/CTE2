from tqdm import tqdm
from ase.build import bulk
from sevenn.calculator import SevenNetCalculator
from ase.calculators.singlepoint import SinglePointCalculator

"""
modified based on Jaesun Kim's code
"""

def get_calc(config):
    conf = config['calculator']
    calc_args = conf.get('calc_args', {})

    print('\n*************************************')
    print(f'calc type: {conf["calc_type"].upper()}')
    print(f'calc: {conf["calc"].upper()}')
    print(f'modal: {calc_args["modal"]}')
    print(f'path: {conf["path"]}')
    print('*************************************\n')

    calc = SevenNetCalculator(model=conf['path'], **calc_args)

    try:
        atoms = bulk('Si')
        atoms.calc = calc
        atoms.get_potential_energy(force_consistent=True)
        print('SevenNetCalculator successfully initiated')

    except:
        calc_args['enable_flash'] = not calc_args['enable_flash']
        calc = SevenNetCalculator(model=conf['path'], **calc_args)
        print('SevenNetCalculator successfully initiated')
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

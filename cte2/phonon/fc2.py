import numpy as np
import gc, os, torch
from tqdm import tqdm
import ase.io as ase_IO

from phonopy import file_IO as ph_IO
from phonopy import load as load_phonon
from phonopy.api_phonopy import Phonopy

from cte2.util.calc import single_point_calculate


def calculate_fc2(phonon, phonon_dir, calc, symm_fc2 = True):
    forces = []
    for idx in range(len(phonon.displacements)):
        label = str(idx+1).zfill(3)
        atoms = ase_IO.read(f"{phonon_dir}/fc2-{label}/POSCAR", format='vasp')
        atoms = single_point_calculate(atoms, calc)
        ase_IO.write(f"{phonon_dir}/fc2-{label}/CONTCAR", atoms, format='vasp')
        forces.append(atoms.get_forces())

    force_set = np.array(forces)
    phonon.forces = force_set
    phonon.produce_force_constants()

    if symm_fc2:
        phonon.symmetrize_force_constants()
    return phonon

def process_fc2(config, calc=None):
    ratio_list = config['deform']['ratio']
    conf = config['phonon']
    save_dir = conf['save']
    symm_fc2 = conf['symm_fc2']

    for i, suffix in enumerate(tqdm(suffix_list, desc='processing fc2')):
        supercell_dir = f"{config['supercell']['save']}/e{i}"
        phonon_dir = f"{save_dir}/e{i}"
        os.makedirs(phonon_dir, exist_ok = True)
        fc2_file = f"{phonon_dir}/FORCE_CONSTANTS_2ND"
        phonon = load_phonon(f"{supercell_dir}/phonopy_disp.yaml")

        if os.path.isfile(fc2_file):
            try:
                fc2 = ph_IO.parse_FORCE_CONSTANTS(fc2_file)
                phonon.force_constants = fc2
            except:
                print(f'WARNING: ERROR while parsing FC2 of the {i}th structure; will re-calculate')
                phonon = calculate_fc2(phonon, phonon_dir, calc)

            ph_IO.write_FORCE_CONSTANTS(phonon.force_constants, filename=fc2_file)

        else:
            phonon = calculate_fc2(phonon, phonon_dir, calc)
            ph_IO.write_FORCE_CONSTANTS(phonon.force_constants, filename=fc2_file)

        torch.cuda.empty_cache()
        gc.collect()
        phonon.save(f'{phonon_dir}/phonopy_params.yaml', compression='xz')



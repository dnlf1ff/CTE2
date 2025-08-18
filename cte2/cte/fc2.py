import numpy as np
import gc, os, torch
from tqdm import tqdm
import ase.io as ase_IO

from phonopy import file_IO as ph_IO
from phonopy import load as load_phonon
from phonopy.api_phonopy import Phonopy

from cte2.util.calc import single_point_calculate
from cte2.util.utils import _get_suffix_list

from typing import Optional, Union, Any

def calculate_fc2(phonon: Phonopy, phonon_dir: Union[str, os.PathLike], calc: Optional[Any]=None, symm_fc2: Union[bool, int]=True):
    forces = []
    for idx in range(len(phonon.displacements)):
        label = str(idx+1).zfill(3)
        if calc is not None:
            ase_IO.read(f"{phonon_dir}/fc2-{label}/POSCAR", atoms, format='vasp')
            atoms = single_point_calculate(atoms, calc)
            ase_IO.write(f"{phonon_dir}/fc2-{label}/CONTCAR", atoms, format='vasp')

        else:
            atoms = ase_IO.read(f"{phonon_dir}/fc2-{label}/OUTCAR")
        forces.append(atoms.get_forces())

    force_set = np.array(forces)
    phonon.forces = force_set
    phonon.produce_force_constants()

    if symm_fc2:
        phonon.symmetrize_force_constants()
    return phonon

def process_fc2(config, calc=None):
    strain_args = {
            'e_min': config['deform']['e_min'],
            'e_max': config['deform']['e_max'],
            'delta': config['deform']['delta'],
            'Nsteps': config['deform']['Nsteps']}

    suffix_list = _get_suffix_list(**strain_args)

    for idx, suffix in enumerate(tqdm(suffix_list, desc='processing fc2')):
        phonon_dir = f"{config['phonon']['save']}/e-{suffix}"
        fc2_dir = f"{config['harmonic']['save']}/e-{suffix}"
        os.makedirs(fc2_dir, exist_ok = True)
        fc2_file = f"{fc2_dir}/FORCE_CONSTANTS_2ND"

        phonon = load_phonon(f"{phonon_dir}/phonopy_disp.yaml")
        if os.path.isfile(fc2_file):
            try:
                fc2 = ph_IO.parse_FORCE_CONSTANTS(fc2_file)
                phonon.force_constants = fc2
            except:
                phonon = calculate_fc2(phonon, phonon_dir, calc)

            ph_IO.write_FORCE_CONSTANTS(
                phonon.force_constants, filename=fc2_file)
        else:
            try:
                fc2 = ph_IO.parse_FORCE_CONSTANTS(fc2_file)
                phonon.force_constants = fc2
            except:
                phonon = calculate_fc2(phonon, phonon_dir)

            ph_IO.write_FORCE_CONSTANTS(
                phonon.force_constants, filename=fc2_file)

        torch.cuda.empty_cache()
        gc.collect()
        phonon.save(f'{fc2_dir}/phonopy_params.yaml', compression='xz')



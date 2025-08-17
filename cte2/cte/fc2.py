import numpy as np
import gc, sys, os, torch
from tqdm import tqdm
from ase.io import read

from cte2.util.utils import _get_suffix_list, aseatoms2phonoatoms

from phonopy.api_phonopy import Phonopy
from phonopy import file_IO as ph_IO
from phonopy import load

from cte2.util.logger import Logger
from cte2.mlip.calc import single_point_calculate_list


def calculate_fc2(config, ph, suffix, calc):
    forces = []
    nat = len(ph.supercell)
    for idx, sc in enumerate(ph.supercells_with_displacements):
        label = str(idx+1).zfill(3)
        if calc is not None:
            atoms = read(f"{config['phonon']['save']}/e-{suffix}/fc2-{label}", format='vasp')
            atoms = single_point_calculate(atoms, calc, desc=desc)
            write(f"{config['phonon']['save']}/e-{suffix}/fc2-{label}/CONTCAR", atoms, format='vasp')

        else:
            atoms = read(f"{config['phonon']['save']}/e-{suffix}/fc2-{label}/OUTCAR")
        forces.append(atoms.get_forces())

    force_set = np.array(forces)
    phonon.forces = force_set
    phonon.produce_force_constants()
    if config['phonon']['symmetrize']:
        phonon.symmetrize_force_constants()
    return phonon

def process_fc2(config, calc=None):
    logger = Logger()

    strain_args = {
            'e_min': config['deform']['e_min'],
            'e_max': config['deform']['e_max'],
            'delta': config['deform']['delta'],
            'Nsteps': config['deform']['Nsteps']}

    suffix_range = _get_suffix_list(**strain_args)


    for idx, suffix in enumerate(tqdm(suffix_range), desc='processing fc2')):
        phonon_dir = f"{config['phonon']['save']}/e-{suffix}"
        fc2_dir = f"{config['harmonic']['save']}/e-{suffix}"
        os.makedirs(fc2_dir, exist_ok = True)

        phonon = load(f"{phonon_dir}/phonopy_disp.yaml")
        if calc is not None:
            phonon.generate_displacements(distance=config['phonon']['distance'], random_seed=config['phonon']['random_seed'])

        try:
            fc2 = ph_IO.parse_FORCE_CONSTANTS(f'{fc2_dir}/FORCE_CONSTANTS_2ND')
            phonon.force_constants = fc2
        except:
            ph = calculate_fc2(config, ph, calc, symmetrize_fc2)
            if save_fc2:
                ph_IO.write_FORCE_CONSTANTS(
                    ph.force_constants,
                    filename=f'{fc2_dir}/FORCE_CONSTANTS_2ND',
                )
        except Exception as e:
            sys.stderr.write(f'FC2 calc error at {idx}-th atoms: {e}\n')
            error = True

        num_fc2 = sum(
            [1 for sc in ph.supercells_with_displacements if sc is not None]
        )

        torch.cuda.empty_cache()
        gc.collect()
        ph.save(f'{fc2_dir}/phonopy_params.yaml', compression='xz')



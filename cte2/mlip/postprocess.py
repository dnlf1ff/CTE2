from cte2.util.logger import Logger
from cte2.util.utils import _get_suffix_list

from phonopy.api_phonopy import Phonopy

import numpy as np
from tqdm import tqdm
import warnings
from ase.io import read, write
import torch, gc
import os

def process_phonon(config, desc='initiating phonopy with primitive matrix'):
    logger = Logger()

    delta, Nsteps = config['deform']['delta'], config['deform']['Nsteps']
    e_min, e_max = config['deform']['e_min'], config['deform']['e_max']
    suffix_list = _get_suffix_list(e_min, e_max, delta=delta, Nsteps=Nsteps)

    for idx, suffix in enumerate(tqdm(suffix_list), desc=desc)):
        prefix = f"{config['phonon']['save']}/e-{suffix}"
        os.makedirs(prefix, exist_ok = True)
        atoms = read(f"{config['deform']['save']}/e-{suffix}/CONTCAR", format='vasp')
        unitcell = aseatoms2phonoatoms(atoms)

        try:
            phonon = Phonopy(
                unitcell=unitcell,
                supercell_matrix=config['fc2']['supercell'],
                symprec= config['phonon']['symprec'],
                primitive_matrix = np.diag(config['phonon']['primitive']).tolist(),
            )
            phonon.generate_displacements(distance=config['fc2']['distance'],
                                  random_seed=config['fc2']['random_seed'])

        except Exception as e:
            sys.stderr.write(f'Error {e} occured at {idx}')
            pm_error = True

            phonon = Phonopy(
                unitcell=unitcell,
                supercell_matrix=config['fc2']['supercell'],
                symprec= config['phonon']['symprec'],
                primitive_matrix = np.diag([1,1,1]).tolist(),
            )
            phonon.generate_displacements(distance=config['fc2']['distance'],
                                  random_seed=config['fc2']['random_seed'])
            for j, sc in enumerate(phonon.supercells_with_displacements):
                label = str(j+1).zfill(3)
                atoms= Atoms(sc.symbols, cell=sc.cell, positions=sc.positions, pbc=True)
                write(f"{prefix}/fc2-{labe}/POSCAR", atoms, format='vasp')

        phonon.save(f"{prefix}/phonopy_disp.yaml")

from cte2.util.logger import Logger
from cte2.util.utils import _get_suffix_list, aseatoms2phonoatoms

from phonopy.api_phonopy import Phonopy

import numpy as np
from tqdm import tqdm
import warnings
import ase.io as ase_IO
from ase import Atoms
import torch, gc, os, sys

def process_phonon(config):
    desc='initiating phonopy with primitive matrix')
    logger = Logger()

    delta, Nsteps = config['deform']['delta'], config['deform']['Nsteps']
    e_min, e_max = config['deform']['e_min'], config['deform']['e_max']
    suffix_list = _get_suffix_list(e_min, e_max, delta=delta, Nsteps=Nsteps)

    for idx, suffix in enumerate(tqdm(suffix_list, desc=desc)):
        phonon_dir = f"{config['phonon']['save']}/e-{suffix}"
        deform_dir = f"{config['deform']['save']}/e-{suffix}"
        os.makedirs(phonon_dir, exist_ok = True)
        atoms = ase_IO.read(f"{deform_dir}/CONTCAR", format='vasp')
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
                ase_IO.write(f"{phonon_dir}/fc2-{label}/POSCAR", atoms, format='vasp')

        phonon.save(f"{phonon_dir}/phonopy_disp.yaml")

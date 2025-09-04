from phonopy.api_phonopy import Phonopy

import numpy as np
from tqdm import tqdm
import ase.io as ase_IO
from ase import Atoms
import os, sys

from cte2.util.utils import aseatoms2phonoatoms
from cte2.util.utils import phonoatoms2aseatoms

def process_supercell(config):
    ratio_list = config['deform']['ratio']
    conf = config['supercell']
    save_dir = conf['save']

    for i in (tqdm(range(len(ratio_list)), desc='Generating displaced supercells with phonopy')):
        supercell_dir = f"{save_dir}/e{i}"
        deform_dir = f"{config['deform']['save']}/e{i}"
        os.makedirs(supercell_dir, exist_ok = True)
        atoms = ase_IO.read(f"{deform_dir}/CONTCAR", format='vasp')
        unitcell = aseatoms2phonoatoms(atoms)

        phonon = Phonopy(
            unitcell=unitcell,
            supercell_matrix=conf['supercell_matrix'],
            symprec= conf['symprec'],
            primitive_matrix = config['unitcell']['primitive_matrix'],
            )
        phonon.generate_displacements(distance=conf['distance'],
                                  random_seed=conf['random_seed'])


        for j, sc in enumerate(phonon.supercells_with_displacements):
            label = str(j+1).zfill(3)
            os.makedirs(f"{supercell_dir}/fc2-{label}", exist_ok=True)
            atoms= phonoatoms2aseatoms(sc)
            ase_IO.write(f"{supercell_dir}/fc2-{label}/POSCAR", atoms, format='vasp')

        phonon.save(f"{supercell_dir}/phonopy_disp.yaml")

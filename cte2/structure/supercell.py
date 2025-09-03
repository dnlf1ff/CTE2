from phonopy.api_phonopy import Phonopy

import numpy as np
from tqdm import tqdm
import ase.io as ase_IO
from ase import Atoms
import os, sys

def process_supercell(config):
    ratio_list = config['deform']['ratio']
    conf = config['supercell']
    save_dir = conf['save']

    for i in (tqdm(range(len(ratio_list)), desc='Generating displaced supercells with phonopy')):
        supercell_dir = f"{config['supercell']['save']}/e{i}"
        deform_dir = f"{config['deform']['save']}/e{i}"
        os.makedirs(supercell_dir, exist_ok = True)
        atoms = ase_IO.read(f"{deform_dir}/CONTCAR", format='vasp')
        unitcell = aseatoms2phonoatoms(atoms)

        try:
            phonon = Phonopy(
                unitcell=unitcell,
                supercell_matrix=conf['supercell_matrix'],
                symprec= conf['symprec'],
                primitive_matrix = config['unitcell']['primitive_matrix'],
            )
            phonon.generate_displacements(distance=conf['distance'],
                                  random_seed=conf['random_seed'])

        except Exception as e:
            sys.stderr.write(f'Error {e} occured at {i}th deformed structure')
            pm_error = True

            phonon = Phonopy(
                unitcell=unitcell,
                supercell_matrix=config['phonon']['supercell'],
                symprec= config['phonon']['symprec'],
                primitive_matrix = np.diag([1,1,1]).tolist(),
            )

            config['phonon']['primitive'] = np.diag([1,1,1]).tolist()
            from cte2.util.io import dumpYAML
            dumpYAML(config, f"{config['dir']['cwd']}/config_re.yaml")
            phonon.generate_displacements(distance=config['phonon']['distance'],
                                  random_seed=config['phonon']['random_seed'])

        for j, sc in enumerate(phonon.supercells_with_displacements):
            label = str(j+1).zfill(3)
            os.makedirs(f"{supercell_dir}/fc2-{label}", exist_ok=True)
            atoms= phonoatoms2aseatoms(sc)
            ase_IO.write(f"{supercell_dir}/fc2-{label}/POSCAR", atoms, format='vasp')

        phonon.save(f"{supercell_dir}/phonopy_disp.yaml")

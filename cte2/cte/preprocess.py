from cte2.util.logger import Logger
from cte2.util.utils import _get_ratio_list, _get_strain_list, _get_suffix_list, get_spgnum, write_csv

import numpy as np
from tqdm import tqdm
import warnings
from ase.io import read, write
import torch, gc
import os

def scale_poscar(config):
    logger = Logger()
    desc = 'Applying strains to unitcell'
    delta, Nsteps = config['deform']['delta'], config['deform']['Nsteps']
    e_min, e_max = config['deform']['e_min'], config['deform']['e_max']

    ratio_list = _get_ratio_list(e_min, e_max, delta=delta, Nsteps=Nsteps)
    suffix_list = _get_suffix_list(e_min, e_max, delta=delta, Nsteps=Nsteps)

    poscar_opt = open(f"{config['unitcell']['save']}/CONTCAR", 'r')
    lines = poscar_opt.readlines()

    for idx, (ratio, suffix) in enumerate(tqdm(zip(ratio_list, suffix_list), desc = desc)):
        deform_dir = f"{config['deform']['save']}/e-{suffix}"
        os.makedirs(deform_dir, exist_ok = True)
        if not config['deform']['load']:
            poscar_file = open(f"{deform_dir}/POSCAR", 'w')
            strained_lines = lines.copy()
            strained_lines[1] = f'{ratio}\n'
            for line in strained_lines:
                poscar_file.write(line)
            poscar_file.close()

        atoms = read(f"{deform_dir}/POSCAR")

    write(config['deform']['save']+f'/deformed.extxyz', 
          [read(f"{config['deform']['save']/e-{suffix}/POSCAR" for suffix in suffix_list, format='vasp')])


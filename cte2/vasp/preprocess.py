from ase.io import read, write
from phonopy.interface.vasp import write_vasp
from tqdm import tqdm
import os, shutil

from pymatgen.io.vasp import Vasprun

from cte2.vasp.io import write_mpr_potcar, write_incar, write_kpoints
from cte2.util.logger import Logger
from cte2.util.utils import _get_suffix_list, write_csv, get_spgnum, get_supercell_from_config, get_primitive_from_config

from cte2.util.config import Essential

from typing import Dict, Any

def update_settings(dct_default, dct_from_config):
    dct = dct_default.copy()
    dct.update(dct_from_config)
    for k, v in dct.items():
        if not isinstance(v, Essential):
            continue
        raise ValueError(f'{k}: {v} must be given')
    return dct

def process_input(config):
    from cte2.vasp.io import INCAR_UNITCELL, KPOINTS_RELAX
    unitcell_dir = config['unitcell']['save']
    incar = update_settings(INCAR_UNITCELL, config['unitcell']['incar'].copy())
    write_incar(incar, unitcell_dir)
    kpoints = update_settings(KPOINTS_RELAX, config['unitcell']['kpoints'].copy())
    write_kpoints(kpoints, unitcell_dir)
    unitcell = read(config['data']['input'], **config['data']['load_args'])

    write(f"{unitcell_dir}/POSCAR", unitcell, format='vasp')
    write_mpr_potcar(poscar_dir=f"{unitcell_dir}/POSCAR", subdir=unitcell_dir, POTCAR_DIR=config['calculator']['potential_dirname'])


def process_deform(config):
    from cte2.vasp.io import INCAR_DEFORMED, KPOINTS_RELAX
    from cte2.cte.preprocess import scale_poscar
    deform_dir = config['deform']['save']

    incar = update_settings(INCAR_DEFORMED, config['deform']['incar'].copy())
    write_incar(incar, deform_dir)
    kpoints = update_settings(KPOINTS_RELAX, config['deform']['kpoints'].copy())
    write_kpoints(kpoints, deform_dir)
    write_mpr_potcar(f"{config['unitcell']['save']}/CONTCAR", subdir=config['deform']['save'], POTCAR_DIR=config['calculator']['potential_dirname'])
    scale_poscar(config)

    strain_args = {
            'e_min': config['deform']['e_min'],
            'e_max': config['deform']['e_max'],
            'delta': config['deform']['delta'],
            'Nsteps': config['deform']['Nsteps']}

    suffix_list = _get_suffix_list(**strain_args)

    for suffix in tqdm(suffix_list, desc='writing vasp input files for strained structures'):
        prefix = f"{deform_dir}/e-{suffix}/"
        shutil.copy(f"{deform_dir}/POTCAR", prefix)
        shutil.copy(f"{deform_dir}/KPOINTS", prefix)
        shutil.copy(f"{deform_dir}/INCAR", prefix)

def process_phonon(config):
    from cte2.vasp.io import INCAR_FORCE, KPOINTS_FORCE
    from phonopy.api_phonopy import Phonopy
    from cte2.util.utils import aseatoms2phonoatoms

    phonon_dir = config['phonon']['save']

    incar = update_settings(INCAR_FORCE, config['phonon']['incar'].copy())
    write_incar(incar, config['phonon']['save'])
    kpoints = update_settings(KPOINTS_FORCE, config['phonon']['kpoints'].copy())
    write_incar(incar, phonon_dir)
    kpoints = update_settings(KPOINTS_FORCE, config['phonon']['kpoints'].copy())
    write_kpoints(kpoints, phonon_dir)
    write_mpr_potcar(f"{config['unitcell']['save']}/POSCAR", subdir=config['phonon']['save'], POTCAR_DIR=config['calculator']['potential_dirname'])
    kpoints_file, incar_file, potcar_file = f"{phonon_dir}/KPOINTS", f"{phonon_dir}/INCAR", f"{phonon_dir}/POTCAR"

    strain_args = {
            'e_min': config['deform']['e_min'],
            'e_max': config['deform']['e_max'],
            'delta': config['deform']['delta'],
            'Nsteps': config['deform']['Nsteps']}

    suffix_list = _get_suffix_list(**strain_args)

    for suffix in tqdm(suffix_list, desc='processing phonon supercells'):
        contcar = read(f'{config["deform"]["save"]}/e-{suffix}/CONTCAR', format='vasp')

        phonon = Phonopy(unitcell=aseatoms2phonoatoms(contcar),
                         supercell_matrix=get_supercell_from_config(config['phonon']['supercell']),
                         primitive_matrix=get_primitive_from_config(config['phonon']['primitive']))

        phonon.generate_displacements()
        phonon.save(f'{phonon_dir}/e-{suffix}/phonopy_disp.yaml')
        supercells = phonon.supercells_with_displacements

        for idx, supercell in enumerate(supercells):
            label = str(int(idx+1)).zfill(3)
            os.makedirs(f'{phonon_dir}/e-{suffix}/fc2-{label}', exist_ok=True)
            write_vasp(f'{phonon_dir}/e-{suffix}/fc2-{label}/POSCAR', supercell)

            shutil.copy(kpoints_file, f'{phonon_dir}/e-{suffix}/fc2-{label}/KPOINTS')
            shutil.copy(incar_file, f'{phonon_dir}/e-{suffix}/fc2-{label}/INCAR')
            shutil.copy(potcar_file, f'{phonon_dir}/e-{suffix}/fc2-{label}/POTCAR')



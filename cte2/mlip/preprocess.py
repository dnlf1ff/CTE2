from cte2.mlip.relax import aar_from_config
from cte2.util.logger import Logger
from cte2.util.utils import _get_strain_list, _get_suffix_list, get_spgnum, write_csv
from cte2.cte.preprocess import scale_poscar

import numpy as np
from tqdm import tqdm
import warnings
from ase.io import read, write
import torch, gc
import os

def process_input(config, calc):
    logger = Logger()
    print('optimizing input atoms\n')
    csv_file = open(f"{config['cwd']}/unitcell.csv", "w", buffering = 1)
    csv_file.write('idx,energy,volume,natom,a,b,c,alpha,beta,gamma,conv\n')
    ase_atom_relaxer = aar_from_config(config, calc, opt=config['unitcell']['opt'])
    atoms = read(config['data']['input'], **config['data']['load_args'])
    atoms.info['init_spg_num'] = init_spg = get_spgnum(atoms)
    atoms = ase_atom_relaxer.update_atoms_info(atoms)
    write_csv(csv_file, atoms)

    if not config['unitcell']['load']:
        atoms = ase_atom_relaxer.relax_atoms(atoms)
        atoms = ase_atom_relaxer.update_atoms_info(atoms)
        atoms.calc = None
        atoms.info['spg_num'] = spg_num = get_spgnum(atoms)
        write(f"{config['unitcell']['save']}/CONTCAR", atoms, format='vasp')

    else:
        atoms = read(config["unitcell"]["load"], format='vasp')
        spg_num = get_spgnum(atoms)

    write_csv(csv_file, atoms, idx='post')
    spg_same = (spg_num == init_spg)

    if not spg_same:
        warnings.warn(
            f'space group number changed while optimizing {atoms} (input structure)'
            + f'{init_spg} > {spg_num}'
            )
    if not atoms.info['conv']:
        step = config['opt'][opt]['steps']
        warnings.warn(
            f'unitcell structure {atoms} did not converged with in {step} steps!'
            )

    unitcell_recorder = {'Formula': atoms.get_chemical_formula(empirical=True), 'Natom': len(atoms),
                        'Conv': atoms.info['conv'], 'SPG_num': spg_num, 'Angle': atoms.cell.angles(),
                        'Length': atoms.cell.lengths()}

    logger.unitcell_recorder.update(dct = unitcell_recorder)
    csv_file.close()
    del ase_atom_relaxer, atoms, csv_file
    gc.collect()

def process_deform(config, calc):
    desc = 'relaxing strained atoms'
    logger = Logger()
    ase_atom_relaxer = aar_from_config(config, calc, opt=config['deform']['opt'])
    csv_file = open(f"{config['cwd']}/{config['deformed']['write']}", "w", buffering = 1)
    csv_file.write('idx,energy,volume,natom,a,b,c,alpha,beta,gamma,conv\n')
    delta, Nsteps = config['deform']['delta'], config['deform']['Nsteps']
    e_min, e_max = config['deform']['e_min'], config['deform']['e_max']

    strain_list = _get_strain_list(e_min, e_max, delta=delta, Nsteps=Nsteps)
    suffix_list = _get_suffix_list(e_min, e_max, delta=delta, Nsteps=Nsteps)

    if not config['deform']['load']:
        scale_poscar(config)

    for idx, (suffix, strain) in enumerate(tqdm(zip(suffix_list, strain_list), desc=desc)):
        prefix = f"{config['deform']['save']}/e-{suffix}"

        atoms = read(f"{prefix}/POSCAR")
        atoms.info['init_spg_num'] = init_spg = get_spgnum(atoms)
        init_vol = atoms.get_volume()
        atoms = ase_atom_relaxer.update_atoms_info(atoms)
        write_csv(csv_file, atoms, idx=f'pre-e-{suffix}')
        
        if not config['deform']['load_opt']:
            atoms = ase_atom_relaxer.relax_atoms(atoms)
            atoms = ase_atom_relaxer.update_atoms_info(atoms)
            spg_num = atoms.info['spg_num'] = get_spgnum(atoms)

        else:
            atoms = read(f"{prefix}/CONTCAR")
            atoms = ase_atom_relaxer.update_atoms_info(atoms)
            spg_num = get_spgnum(atoms)

        volume = atoms.get_volume()

        write_csv(csv_file, atoms, idx=f'post-e-{strain}')
        write(f"{prefix}/CONTCAR", atoms, format='vasp')

        if not (init_spg == spg_num):
            warnings.warn(
                f'space group number changed while optimizing {idx}-th {atoms} (input structure)'
                + f'{init_spg} > {spg_num}'
            )

        if not (init_vol == volume):
            relax_conf = config["opt"][config["deform"]["opt"]]
            warnings.warn(
                f'volume of cell changed while optimizing {atoms} with ASE {relax_conf["filter"]} filter and mask {relax_conf["mask"]}'
                + f'{init_vol} > {volume}'
                )

        if not atoms.info["conv"]:
            step = config['opt'][opt]['steps']
            warnings.warn(
                f'{idx}-th structure {atoms} did not converged with in {step} steps!'
            )

        deform_recorder = {'Index': idx, 'Strain': strain, 'Conv': atoms.info['conv'], 
                             'SPG_num': spg_num, 'Angle': atoms.cell.angles(), 'Length': atoms.cell.lengths(),
                             'Energy': atoms.info['e_fr_energy'], 'Volume': atoms.get_volume()}

        logger.deform_recorder.update(deform_recorder, idx=idx)

    csv_file.close()
    del csv_file, ase_atom_relaxer

    write(config['deform']['save']+f'/deformed_opt.extxyz', 
          [read(f"{config['deform']['save']/e-{suffix}/CONTCAR" for suffix in suffix_list, format='vasp')])


    torch.cuda.empty_cache()
    gc.collect()



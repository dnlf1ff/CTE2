import ase.io  as ase_IO
from ase import Atoms
from ase.cell import Cell

from tqdm import tqdm
import os, shutil, gc, warnings

from pymatgen.io.vasp import Vasprun
from cte2.util.logger import Logger
from cte2.util.utils import _get_suffix_list, write_csv, get_spgnum


from typing import Dict, Any

def post_unitcell(config):
    logger = Logger()

    csv_file = open(f"{config['unitcell']['save']}/{config['deform']['write']}", "w", buffering=1)
    csv_file.write('idx,energy,volume,natom,a,b,c,alpha,beta,gamma,conv\n')
    vrun = Vasprun(f"{config['unitcell']['save']}/vasprun.xml")
    write_csv(csv_file, vrun, idx='pre')
    write_csv(csv_file, vrun, idx='post')

    atoms = ase_IO.read(f"{config['unitcell']['save']}/POSCAR", format='vasp')
    init_spg = get_spgnum(atoms)
    outcar = ase_IO.read(f"{config['unitcell']['save']}/OUTCAR")
    spg_num = get_spgnum(outcar)

    spg_same = (spg_num == init_spg)

    if not spg_same:
        warnings.warn(
            f'space group number changed while optimizing {atoms} (input structure)'
            + f'{init_spg} > {spg_num}'
            )
    if not vrun.converged:
        incar = config['unitcell']['incar']
        warnings.warn(
                f'unitcell structure {atoms} did not converged with in incar: {incar}'
            )

    unitcell_recorder = {'Formula': outcar.get_chemical_formula(empirical=True), 'Natom': len(outcar),
                        'Conv': vrun.converged, 'SPG_num': spg_num, 'Angle': outcar.cell.angles(),
                        'Length': outcar.cell.lengths()}

    logger.unitcell_recorder.update(dct = unitcell_recorder)
 
    del atoms, vrun, outcar, csv_file
    gc.collect()

def post_deform(config):
    logger = Logger()

    strain_args = {
            'e_min': config['deform']['e_min'],
            'e_max': config['deform']['e_max'],
            'delta': config['deform']['delta'],
            'Nsteps': config['deform']['Nsteps']}

    suffix_list = _get_suffix_list(**strain_args)
    csv_file = open(f"{config['deform']['save']}/{config['deform']['write']}", "w", buffering=1)
    csv_file.write('idx,energy,volume,natom,a,b,c,alpha,beta,gamma,conv\n')

    for idx, suffix in enumerate(tqdm(suffix_list, desc='writing e-v.csv file')):
        deform_dir = f"{config['deform']['save']}/e-{suffix}"

        vrun = Vasprun(f"{deform_dir}/vasprun.xml")
        write_csv(csv_file, vrun, idx='pre')
        write_csv(csv_file, vrun, idx='post')

        atoms = ase_IO.read(f"{deform_dir}/POSCAR", format='vasp')
        init_spg = get_spgnum(atoms)
        init_vol = atoms.get_volume()
        outcar = ase_IO.read(f"{deform_dir}/OUTCAR")
        spg_num = get_spgnum(outcar)
        volume = outcar.get_volume()

        if not (init_spg == spg_num):
            warnings.warn(
                f'space group number changed while optimizing {atoms} (input structure)'
                + f'{init_spg} > {spg_num}'
                )

        if not (init_vol == volume):
            warnings.warn(
                f'volume of cell changed while optimizing {atoms} with ISIF = 2'
                + f'{init_vol} > {volume}'
                )

        if not vrun.converged:
            incar = config['deform']['incar']
            warnings.warn(
                    f'unitcell structure {atoms} did not converged with in incar: {incar}'
                )

            deform_recorder = {'Index': idx, 'Conv': vrun.converged, 'SPG_num': spg_num,
                               'Angle': outcar.cell.angles(), 'Length': outcar.cell.lengths(),
                               'Energy': outcar.get_potential_energy(force_consistent=True), 'Volume': volume}

            logger.deform_recorder.update(dct = deform_recorder, idx=idx)

        del atoms, vrun, outcar
        gc.collect()
    csv_file.close()



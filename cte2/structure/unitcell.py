from cte2.util.relax import aar_from_config
from cte2.cte.preprocess import scale_poscar

import numpy as np
from tqdm import tqdm
import ase.io as ase_IO
import torch, gc

def process_input(config, calc):
    print('optimizing input atoms\n')
    save_dir = config['unitcell']['save']
    ase_logfile = f'{save_dir}/unitcell.log' 

    csv_file = open(f"{struct_dir}/unitcell_relaxation.csv", "w", buffering = 1)
    csv_file.write('idx,energy,volume,natom,a,b,c,alpha,beta,gamma,conv\n')

    ase_atom_relaxer = aar_from_config(config, calc, opt_type='unitcell', logfile=logfile)
    atoms = ase_IO.read(config['data']['input'], **config['data']['load_args'])

    init_spg = get_spgnum(atoms)
    atoms = ase_atom_relaxer.update_atoms(atoms)
    write_csv(csv_file, atoms)

    if not config['unitcell']['load']:
        atoms = ase_atom_relaxer.relax_atoms(atoms)
        atoms = ase_atom_relaxer.update_atoms(atoms)
        atoms.calc = None
        spg_num = get_spgnum(atoms)
        ase_IO.write(f"{save_dir}/CONTCAR", atoms, format='vasp')

    else:
        atoms = ase_IO.read(config["unitcell"]["load"], format='vasp')
        spg_num = get_spgnum(atoms)

    write_csv(csv_file, atoms, idx='post')

    if not (init_spg == spg_num):
        print('WARNING: space group number changed while relaxing unitcell {init_spg} > {spg_num}')

    if not atoms.info['conv']:
        step = config['opt'][unitcell]['steps']
        print(f'WARNING: unitcell structure did not converged with in {step} steps!')

    csv_file.close()
    del ase_atom_relaxer, atoms, csv_file
    gc.collect()


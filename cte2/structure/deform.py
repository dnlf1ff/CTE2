
from tqdm import tqdm
import ase.io as ase_IO
import torch, gc, os

from cte2.util.utils import get_spgnum, write_csv
from cte2.util.relax import get_ase_relaxer

def scale_unitcell(config):
    save_dir = config['deform']['save']
    ratio_list = config['deform']['ratio']

    if config['deform']['load']:
        return

    poscar_opt = open(f"{config['unitcell']['save']}/CONTCAR", 'r')
    lines = poscar_opt.readlines()
    for i, ratio in tqdm(enumerate(ratio_list), desc='Applying strain to unitcell'):
        deform_dir = f"{save_dir}/e{i}"
        os.makedirs(deform_dir, exist_ok = True)
        if not config['deform']['load']:
            poscar_file = open(f"{deform_dir}/POSCAR", 'w')
            strained_lines = lines.copy()
            strained_lines[1] = f'{ratio}\n'
            for line in strained_lines:
                poscar_file.write(line)
            poscar_file.close()
    return

def process_deform(config, calc):
    save_dir = config['deform']['save']
    ratio_list = config['deform']['ratio']

    csv_file = open(f"{save_dir}/deformed.csv", "w", buffering = 1)
    csv_file.write('idx,energy,volume,natom,a,b,c,alpha,beta,gamma,conv\n')

    scale_unitcell(config)

    for i in tqdm(range(len(ratio_list)), desc='Relaxing strained(deformed) unitcells'):
        deform_dir = f"{save_dir}/e{i}"

        ase_relaxer = get_ase_relaxer(config, calc, opt_type='deform', logfile=f"{deform_dir}/relax.log")
        atoms = ase_IO.read(f"{deform_dir}/POSCAR")
        init_spg = get_spgnum(atoms)
        atoms = ase_relaxer.update_atoms(atoms)
        write_csv(csv_file, atoms, idx=f'pre-{i}')
        
        if not config['deform']['load_opt']:
            atoms = ase_relaxer.relax_atoms(atoms)
            atoms = ase_relaxer.update_atoms(atoms)
            spg_num = get_spgnum(atoms)

        else:
            atoms = ase_IO.read(f"{deform_dir}/CONTCAR")
            atoms = ase_relaxer.update_atoms(atoms)
            spg_num = get_spgnum(atoms)

        write_csv(csv_file, atoms, idx=f'post-{i}')
        ase_IO.write(f"{deform_dir}/CONTCAR", atoms, format='vasp')

        if not (init_spg == spg_num):
            print('WARNING: space group number changed while relaxing {i}th deformed structure {init_spg} > {spg_num}')

        if not atoms.info["conv"]:
            step = config['opt']['deform']['steps']
            print(f'WARNING: {i}th deformed structure did not converged with in {step} steps!')

    csv_file.close()
    del csv_file

    torch.cuda.empty_cache()
    gc.collect()


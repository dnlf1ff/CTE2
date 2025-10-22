from tqdm import tqdm
import ase.io as ase_IO
import torch, gc, os

from cte2.util.utils import get_spgnum, write_csv
from cte2.util.relax import get_ase_relaxer
from cte2.util.io import dumpPKL

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
    atoms_list = []

    csv_file = open(f"{save_dir}/deformed.csv", "w", buffering = 1)
    csv_file.write('idx,ratio,init_sgn,sgn,energy,volume,natom,a,b,c,alpha,beta,gamma,force_conv,steps,opt_conv\n')

    scale_unitcell(config)
    
    deform_dct = {}

    for i, ratio in tqdm(enumerate(ratio_list), desc='Relaxing strained(deformed) unitcells'):
        deform_dir = f"{save_dir}/e{i}"
        deform_dct[i] = {'pre': {}, 'post': {}}

        ase_relaxer = get_ase_relaxer(config, calc, opt_type='deform', logfile=f"{deform_dir}/relax.log")
        atoms = ase_IO.read(f"{deform_dir}/POSCAR")
        init_spg = get_spgnum(atoms)
        atoms = ase_relaxer.update_atoms(atoms)
        atoms.info['init_sgn'] = init_spg
        atoms.info['task'] = 'unitcell optimization'
        atoms.info['ratio'] = ratio
        atoms.info['strain'] = float(ratio)-1
        atoms.info['index'] = i
        atoms.info['sgn'] = '#N/A'
        atoms.info['opt'] = 'pre'
        atoms.info['opt_conv'] = '#N/A'
        atoms.info['opt_steps'] = '#N/A'
        atoms.info['force_conv'] = '#N/A'
        atoms_list.append(atoms)

        if not config['deform']['load_opt']:
            atoms = ase_relaxer.relax_atoms(atoms)
            atoms = ase_relaxer.update_atoms(atoms)
            spg_num = get_spgnum(atoms)

            if atoms.info['opt_conv']:
                deform_dct['post'].update(atoms.info.copy())
                spg_num = get_spgnum(atoms)
                write_csv(csv_file, atoms, idx=f'post-{i}')
                atoms.calc = None
                ase_IO.write(f"{deform_dir}/CONTCAR", atoms, format='vasp')
                atoms_list.append(atoms)

            else:
                atoms = ase_relaxer.redo(atoms)
                spg_num = get_spgnum(atoms)
                deform_dct['post_re'].update(atoms.info.copy())
                write_csv(csv_file, atoms, idx='post-{i}_re')
                atoms.calc = None
                atoms_list.append(atoms)
                ase_IO.write(f"{deform_dir}/CONTCAR", atoms, format='vasp')
                if not atoms.info['opt_conv']:
                    print('WARNING: failed volume-fixed structural relaxation.')


        else:
            atoms = ase_IO.read(f"{deform_dir}/CONTCAR")
            atoms = ase_relaxer.update_atoms(atoms)
            spg_num = get_spgnum(atoms)

            atoms.info['sgn'] = spg_num
            deform_dct[i]['post'].update(atoms.info.copy())
            write_csv(csv_file, atoms, idx=f'post-{i}')
            atoms_list.append(atoms)

        if not (init_spg == spg_num):
            print('WARNING: space group number changed while relaxing {i}th deformed structure {init_spg} > {spg_num}')

        if not atoms.info["opt_conv"]:
            step = config['opt']['deform']['steps']
            print(f'WARNING: {i}th deformed structure did not converged with in {step} steps!')
        del ase_relaxer

    csv_file.close()
    del csv_file
    dumpPKL(deform_dct, filename=f'{save_dir}/deform_dct.pkl')
    ase_IO.write(f'{save_dir}/deform_opt.extxyz', atoms_list, format='extxyz')

    torch.cuda.empty_cache()
    gc.collect()

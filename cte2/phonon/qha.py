import os
import os.path as osp
from phonopy.api_qha import PhonopyQHA
from phonopy.file_IO import read_thermal_properties_yaml, read_v_e
from contextlib import redirect_stdout, redirect_stderr
import numpy as np
import ase.io as ase_IO

from cte2.util.calc import single_point_calculate
from cte2.util.io import DatToCsv

def process_qha(config, calc):
    # -------- preprocess --------- #
    ratio_list = config['deform']['ratio']
    conf = config['qha']
    qha_dir = config['qha']['save']
    qha_plot = f"{qha_dir}/{conf['plot']}"
    qha_data = f"{qha_dir}/{conf['data']}"
    qha_full = f"{qha_dir}/{conf['full']}"
    prim_factor = np.linalg.det(np.array(config['unitcell']['primitive_matrix']))

    ev_filename = f"{qha_dir}/e-v.dat" # phonopy default setting

    filenames= []
    ev_file = open(ev_filename, 'w', buffering = 1)

    thin_number = config['qha']['thin_number']

    for i, ratio in enumerate(ratio_list):
        phonon_dir = f"{config['phonon']['save']}/e{i}"
        deform_dir = f"{config['deform']['save']}/e{i}"

        if osp.exists(f'{phonon_dir}/ERROR-IMAGINARY.txt'):
             print(f'WARNING: {i}th structure has IMAGINARY modes. Skipping ...')
             continue

        filenames.append(f'{phonon_dir}/thermal_properties.yaml')
        atoms = single_point_calculate(atoms=ase_IO.read(f"{deform_dir}/CONTCAR",format='vasp'),calc=calc)

        ev_file.write(f'{atoms.get_volume()*prim_factor}{chr(9)}{atoms.get_potential_energy()*prim_factor}\n')

    ev_file.close()
    temperatures, cv, entropy, fe_phonon, _, _ = read_thermal_properties_yaml(filenames=filenames)
    temperatures = np.array(temperatures, dtype=float)
    cv = np.array(cv, dtype=float)
    entropy = np.array(entropy, dtype=float)
    fe_phonon = np.array(fe_phonon, dtype=float)

    volumes, free_energies = read_v_e(filename=ev_filename)

    qha_kwargs = {'volumes': volumes, 'electronic_energies': free_energies,
                  'temperatures': temperatures, 'free_energy': fe_phonon,
                  'cv': cv, 'entropy': entropy, 'eos': conf['eos'], 't_max': conf['t_max'],
                  'verbose': True}

    with open(f'{qha_dir}/qha.x', 'w') as f, redirect_stdout(f), redirect_stderr(f):
        qha = PhonopyQHA(**qha_kwargs)
   
    # plot everything at once
    print('plotting qha results')
    os.chdir(qha_plot)
    qha.plot_qha(thin_number=thin_number).savefig(f'{qha_dir}/qha_plot.png', dpi=300)
    qha.plot_qha(thin_number=thin_number).savefig(f'{qha_full}/qha_plot.png', dpi=300)
    qha.plot_pdf_helmholtz_volume(thin_number=thin_number)
    qha.plot_pdf_volume_temperature()
    qha.plot_pdf_thermal_expansion()
    qha.plot_pdf_gibbs_temperature()
    qha.plot_pdf_bulk_modulus_temperature()

    try:
        qha.plot_pdf_heat_capacity_P_polyfit()
        qha.plot_pdf_heat_capacity_P_numerical()
    except Exception as exc:
        print(exc)

    qha.plot_pdf_gruneisen_temperature()

    # save dat files at once
    print('writting down qha data')
    os.chdir(qha_data)
    qha.write_helmholtz_volume()
    qha.write_helmholtz_volume_fitted(thin_number=thin_number)
    qha.write_volume_temperature()
    qha.write_thermal_expansion()
    qha.write_gibbs_temperature()
    qha.write_bulk_modulus_temperature()

    try:
        qha.write_heat_capacity_P_numerical()
        qha.write_heat_capacity_P_polyfit()
    except Exception as exc:
        print(exc)

    qha.write_gruneisen_temperature()

    # thin_numbers were set for readability, plot entire data
    os.chdir(qha_full)
    qha.write_helmholtz_volume_fitted(thin_number=config['phonon']['t_step'])
    qha.plot_pdf_helmholtz_volume(thin_number=config['phonon']['t_step'])

    os.chdir(qha_dir)
    # plot eos
    qha._bulk_modulus.plot().savefig(f'{qha_dir}/{conf["eos"]}.png', dpi=300)

    inp_dat = f'{qha_data}/thermal_expansion.dat'
    out_csv = f'{qha_dir}/thermal_expansion.csv'
    DatToCsv(inp_dat, out_csv, columns='temperature,cte')

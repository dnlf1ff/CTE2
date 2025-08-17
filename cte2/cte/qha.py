import os
import os.path as osp
from phonopy.api_qha import PhonopyQHA
from phonopy.file_IO import read_thermal_properties_yaml, read_v_e
from contextlib import redirect_stdout, redirect_stderr
import pandas as pd
import ase.io as ase_IO
import warnings
from cte2.util.utils import _get_suffix_list
from cte2.util.io import DatToCsv
from cte2.util.calc import single_point_calculate

def process_qha(config, calc=None):
    # -------- preprocess --------- #
    strain_args = {
            'e_min': config['deform']['e_min'],
            'e_max': config['deform']['e_max'],
            'delta': config['deform']['delta'],
            'Nsteps': config['deform']['Nsteps']}

    suffix_list = _get_suffix_list(**strain_args)
    qha_dir = config['qha']['save']
    qha_plot = config['qha']['plot']
    qha_data = config['qha']['data']
    qha_full = config['qha']['full']
    ev_filename = f"{config['qha']['save']}/{config['qha']['write']}"

    filenames= [] 
    ev_file = open(ev_filename, 'w', buffering = 1)

    if 'thin_number' in config['qha'].keys():
        thin_number = config['qha']['thin_number']
    elif 'sparse' in config['qha'].keys():
        thin_number = config['qha']['sparse']
    elif 't_step' in config['qha'].keys():
        warnings.warn('Using t_step as thin_number ... that F-V plots gonna be ugly')
        thin_number = config['qha']['t_step']
    else:
        warnings.warn('No thin_number or sparse or t_step found in config, using default value of 100')
        thin_number = 100

    for idx, suffix in enumerate(suffix_list):
        harmonic_dir = f"{config['harmonic']['save']}/e-{suffix}"
        deform_dir = f"{config['deform']['save']}/e-{suffix}"

        if osp.exists(f'{harmonic_dir}/ERROR-IMAGINARY.txt'):
             warnings.warn(f'WARNING: {harmonic_dir}/ERROR-IMAGINARY.txt exists, skipping this suffix')
             continue

        filenames.append(f'{harmonic_dir}/thermal_properties.yaml')
        if calc is not None:
             atoms = single_point_calculate(atoms=ase_IO.read(f"{deform_dir}/OUTCAR"))
        else:
             atoms = single_point_calculate(atoms=ase_IO.read(f"{deform_dir}/CONTCAR",format='vasp'),calc=calc)

        ev_file.write(f'{atoms.get_volume()}{chr(9)}{atoms.get_potential_energy()}\n')
         
    temperatures, cv, entropy, fe_phonon, _, _ = read_thermal_properties_yaml(filenames=filenames)
    volumes, free_energies = read_v_e(filename=ev_filename)

    qha_kwargs = {'volumes': volumes, 'electronic_energies': free_energies,
                  'temperatures': temperatures, 'free_energy': fe_phonon,
                  'cv': cv, 'entropy': entropy, 'eos': config['qha']['eos'], 't_max': config['qha']['t_max'],
                  'verbose': True}

    with open(f'{qha_dir}/qha.x', 'w') as f, redirect_stdout(f), redirect_stdout(f):
        qha = PhonopyQHA(**qha_kwargs)
   
    os.chdir(qha_plot)
    # gotta plot 'em all
    qha.plot_qha(thin_number=thin_number).savefig(f'{qha_dir}/qha_plot.png', dpi=600)
    qha.plot_qha(thin_number=thin_number).savefig(f'{qha_full}/qha_plot.png', dpi=600)
    qha.plot_pdf_helmholtz_volume(thin_number=thin_number)
    qha.plot_pdf_volume_temperature()
    qha.plot_pdf_thermal_expansion()
    qha.plot_pdf_gibbs_temperature()
    qha.plot_pdf_bulk_modulus_temperature()
    qha.plot_pdf_heat_capacity_P_polyfit()
    qha.plot_pdf_heat_capacity_P_numerical()
    qha.plot_pdf_gruneisen_temperature()

    os.chdir(qha_data)
    qha.write_helmholtz_volume()
    qha.write_helmholtz_volume_fitted(thin_number=thin_number)
    qha.write_volume_temperature()
    qha.write_thermal_expansion()
    qha.write_gibbs_temperature()
    qha.write_bulk_modulus_temperature()
    qha.write_heat_capacity_P_numerical()
    qha.write_heat_capacity_P_polyfit()
    qha.write_gruneisen_temperature()

    os.chdir(qha_full)
    qha.write_helmholtz_volume_fitted(thin_number=config['qha']['t_step'])
    qha.plot_pdf_helmholtz_volume(thin_number=config['qha']['t_step'])

    os.chdir(qha_dir)
    bulk_modulus = qha._bulk_modulus.plot().savefig(f'{qha_dir}/{config["qha"]["eos"]}.png', dpi=600)

    inp_dat = f'{qha_data}/thermal_expansion.dat'
    out_csv = f'{qha_dir}/thermal_expansion.csv'
    DatToCsv(inp_dat, out_csv, columns='temperature,cte')


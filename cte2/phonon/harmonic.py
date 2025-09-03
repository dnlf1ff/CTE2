from __future__ import annotations
import warnings
from phonopy import load
import phonopy.file_IO as ph_IO
import os
from tqdm import tqdm

def process_harmonic(config):
    ratio_list = config['deform']['ratio']
    conf = config['phonon']
    save_dir = conf['save']

    for i, ratio in enumerate(tqdm(ratio_list, desc='calculating harmonic properties')):
        Im = False
        phonon_dir = f"{save_dir}/e{i}"

        if os.path.isfile(f"{h_dir}/phonopy_params.yaml"):
            phonon = load(f"{h_dir}/phonopy_params.yaml")

        else:
            phonon = load(f"{h_dir}/phonopy_params.yaml.xz")

        phonon.force_constants = ph_IO.parse_FORCE_CONSTANTS(f"{h_dir}/FORCE_CONSTANTS_2ND")
        mesh_numbers = config['phonon']['mesh_numbers'] 

        mesh_args = {'is_time_reversal': True, 'is_mesh_symmetry': True,
                        'is_gamma_center': False, 'with_eigenvectors': False,
                        'with_group_velocities': True} # with_eigen_vectors; disable mesh_sym
        phonon.run_mesh(mesh_numbers, **mesh_args)

        phonon.mesh.write_yaml(filename=f'{h_dir}/mesh.yaml')
        frequencies = phonon.get_mesh_dict()['frequencies']

        if check_imaginary_freqs(frequencies):
            with open(f'{h_dir}/ERROR-IMAGINARY.txt', 'w') as f:
                f.write('Imaginary mode detected during {i}th mesh calculation..\n')
                f.close()
            print(f'WARNING: Imaginary mode detected in {i}th deformed structure..')
            Im = True

        if Im:
            continue

        try:
            ph_IO.read_thermal_properties_yaml(filenames=[f"{h_dir}/thermal_properties.yaml"])

        except:
            print(f"Error while parsing thermal properties of {i}th structure")
            print(f"Will calculate the thermal properties again")

            phonon.run_thermal_properties(t_min = conf['t_min'],
                                      t_max=conf['t_max'],
                                      t_step=conf['t_step'])

            phonon.write_yaml_thermal_properties(f'{h_dir}/thermal_properties.yaml')
            thermal_plt = phonon.plot_thermal_properties()
            thermal_plt.savefig(f'{h_dir}/thermal_properties.png', dpi=300)
            thermal_plt.close()

        if conf['run_band']:
            phonon.auto_band_structure(write_yaml=True, filename=f'{h_dir}/band.yaml')
            band_plt = phonon.plot_band_structure()
            band_plt.savefig(f'{h_dir}/band_structure.png', dpi=300)
            band_plt.close()

        if conf['run_dos']:
            mesh_numbers = conf['mesh_numbers']

            phonon.auto_total_dos(filename=f'{h_dir}/total_dos.dat', mesh=mesh_numbers)
            dos_plt = phonon.plot_total_dos()
            dos_plt.savefig(f'{h_dir}/total_dos.png', dpi=300)
            dos_plt.close()
            band_dos_plt = phonon.plot_band_structure_and_dos()
            band_dos_plt.savefig(f'{h_dir}/band_dos.png', dpi=300)
            band_dos_plt.close()
            phonon.save(f'{h_dir}/phonopy.yaml', compression=True)


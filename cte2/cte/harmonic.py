from __future__ import annotations
import warnings
from phonopy import load
import phonopy.file_IO as ph_IO
import os
from tqdm import tqdm

from cte2.util.logger import Logger
from cte2.util.utils import _get_suffix_list, check_imaginary_freqs

def process_harmonic(config):
    logger = Logger()
    strain_args = {
            'e_min': config['deform']['e_min'],
            'e_max': config['deform']['e_max'],
            'delta': config['deform']['delta'],
            'Nsteps': config['deform']['Nsteps']}

    suffix_range = _get_suffix_list(**strain_args)

    for idx, suffix in enumerate(tqdm(suffix_range, desc='calculating harmonic properties')):
        Im = False
        h_dir = f"{config['harmonic']['save']}/e-{suffix}"

        if os.path.isfile(f"{h_dir}/phonopy_params.yaml"):
            phonon = load(f"{h_dir}/phonopy_params.yaml")

        else:
            phonon = load(f"{h_dir}/phonopy_params.yaml.xz")

        phonon.force_constants = ph_IO.parse_FORCE_CONSTANTS(f"{h_dir}/FORCE_CONSTANTS_2ND")
        mesh_numbers = config['harmonic']['mesh_numbers'] 

        mesh_args = {'is_time_reversal': True, 'is_mesh_symmetry': True,
                        'is_gamma_center': False, 'with_eigenvectors': False,
                        'with_group_velocities': True} # with_eigen_vectors; disable mesh_sym
        phonon.run_mesh(mesh_numbers, **mesh_args)

        phonon.mesh.write_yaml(filename=f'{h_dir}/mesh.yaml')
        frequencies = phonon.get_mesh_dict()['frequencies']
        if check_imaginary_freqs(frequencies):
            with open(f'{h_dir}/ERROR-IMAGINARY.txt', 'w') as f:
                f.write('Imaginary mode detected during mesh calculation suffix {suffix}..\n')
                f.close()
            warnings.warn(f'Imaginary mode detected during mesh calculation suffix {suffix}..')
            Im = True
        
        pm_round = [[round(x, 2) for x in param] for param in config['phonon']['primitive']]
        sm_round = [int(x) for x in config['phonon']['supercell']]
        num_disp = int(len(phonon.supercells_with_displacements))

        phonon_recorder = {'Index': idx, 'PM': pm_round, 'FC2':f'{sm_round}*{num_disp}',
                    'Mesh': mesh_numbers, 'Im': IM}
        logger.phonon_recorder.update(phonon_recorder, idx=idx)

        if Im:
            continue

        try:
            ph_IO.read_thermal_properties_yaml(filenames=[f"{h_dir}/thermal_properties.yaml"])

        except Exception as e:
            print(f"Error {e} while reading thermal properties yaml file at e-{suffix} structure")
            print(f"Will calculate thermal properties again")

            phonon.run_thermal_properties(t_min = config['harmonic']['t_min'],
                                      t_max=config['harmonic']['t_max'],
                                      t_step=config['harmonic']['t_step'])

            phonon.write_yaml_thermal_properties(f'{h_dir}/thermal_properties.yaml')
            thermal_plt = phonon.plot_thermal_properties()
            thermal_plt.savefig(f'{h_dir}/thermal_properties.png', dpi=300)
            thermal_plt.close()

        if config['harmonic']['band']:
            phonon.auto_band_structure(write_yaml=True, filename=f'{h_dir}/band.yaml')
            band_plt = phonon.plot_band_structure()
            band_plt.savefig(f'{h_dir}/band_structure.png', dpi=300)
            band_plt.close()

        if config['harmonic']['dos']:
            dos_args = {'mesh': mesh_numbers, 'is_time_reversal': True, 'is_mesh_symmetry': True,
                        'is_gamma_center': False, 'with_tight_requency_range': False, 'write_dat': True}
            phonon.auto_total_dos(filename=f'{h_dir}/total_dos.dat', **dos_args)
            dos_plt = phonon.plot_total_dos()
            dos_plt.savefig(f'{h_dir}/total_dos.png', dpi=300)
            dos_plt.close()
            band_dos_plt = phonon.plot_band_structure_and_dos()
            band_dos_plt.savefig(f'{h_dir}/band_dos.png', dpi=300)
            band_dos_plt.close()
            phonon.save(f'{h_dir}/phonopy.yaml', compression=True)

        if config['harmonic']['pdos']:
            phonon.auto_projected_dos(mesh=mesh_numbers, write_dat=True, filename=f'{h_dir}/projected_dos.dat')
            pdos_plt = phonon.plot_projected_dos()
            pdos_plt.savefig(f'{h_dir}/projected_dos.png', dpi=300)
            pdos_plt.close()
            band_pdos_plt = phonon.plot_band_structure_and_dos()
            band_pdos_plt.savefig(f'{h_dir}/band_pdos.png', dpi=300)
            band_pdos_plt.close()



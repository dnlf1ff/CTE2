DEFAULT_OPT_ARGS = {
    'fmax': 1e-3,
    'steps': 1000,
    'optimizer': 'fire2',
    'cell_filter': 'unitcell',
    'mask': [1,1,1,0,0,0],
    'fix_symm': True,
    'fix_atom': False,
    'logfile': 'relax.log',
}

DEFAULT_CALC_CONFIG = {
    'calc_type': 'fp',
    'functional': 'pbe',
    'potential_dirname': '.',
    'dispersion': False,
    'model': 'vasp',
    'modal': 'pbe54',
    'calc_args': {'device': 'cpu'},
    }


DEFAULT_DATA_CONFIG = {
    'input': input_dir,
    'load_args': {format='vasp', 'index': 0},
}


DEFAULT_UNITCELL_CONFIG = {
    'run': True,
    'load': None,
    'write': 'unitcell.csv',
    'save': './unitcell',
    'opt': DEFAULT_OPT_ARGS,
}


DEFAULT_DEFORM_CONFIG = {
    'save': './deform',
    'write': 'deform.csv', 
    'opt': DEFAULT_OPT_ARGS,
    'run': True,
    'load': None,
    'load_opt': None,
    'delta': 0.02, 
    'Nsteps': 5, 
    'e_min': -0.04, 
    'e_max': 0.04, 
}

DEFAULT_PHONON_CONFIG = {
    'load': None,
    'save': './phonon',
    'primitive': [1, 1, 1],
    'symprec': 1e-05,
    'supercell': [3,3,3], 
    'symmtrize': True,
    'distance': 0.01, 
    'random_seed': 42, 
}


DEFAULT_HARMONIC_CONFIG = {
    'save': './harmonic',
    'fc2': True,
    'mesh': True,
    'mesh_numbers': [48, 48, 48],
    'dos': True,
    'band': True
    'symprec': 1e-05,
    't_min': 0,
    't_max': 501,
    't_step': 25,
}


DEFAULT_QHA_CONFIG = {
    'save': './qha',
    'write': 'e-v.dat',
    't_max': 501,
    'sparse': 50,
    'data': './data',
    'plot': './plot',
    'full': './full',
    'eos': 'birch-murnahghan',
}


if __name__ == "__main__":
    import yaml
    from pathlib import Path

    from cte2.util.io import dumpYAML

    vasp_config = Path(__file__).resolve().parent.parent / 'test-input/vasp_config.yaml'
    zero_config = Path(__file__).resolve().parent.parent / 'test-input/mlip_config.yaml'
    ompa_config = Path(__file__).resolve().parent.parent / 'test-input/mlip_config.yaml'

    key_parse_pair = {
        'data': DEFAULT_DATA_CONFIG,
        'calculator': DEFAULT_CALC_CONFIG,
        'unitcell': DEFAULT_UNITCELL_CONFIG,
        'deform': DEFAULT_DEFORM_CONFIG,
        'phonon': DEFAULT_PHONON_CONFIG,
        'harmonic': DEFAULT_THERMAL_CONFIG,
        'qha': DEFAULT_QHA_CONFIG,
    }

    configs = [vasp_config, zero_config, ompa_config]

    for key, default_config in key_parse_pair.items():
        for i in range(len(configs)):
            config = configs.pop(0)
            config[key] = default_config
            configs.append(config)

    dumpYAML(config, vasp_config)
    dumpYAML(config, zero_config)
    dumpYAML(config, ompa_config)


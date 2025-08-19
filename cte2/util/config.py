import os
from cte2.util.parse_calc_config import check_calc_config
from cte2.util.argparser import parse_args

class Essential:
    pass

DEFAULT_OPT_ARGS = {
    'fmax': 1e-6,
    'steps': 10000,
    'optimizer': 'fire',
    'cell_filter': None,
    'mask': None,
    'fix_symm': True,
    'fix_atom': False,
    'logfile': 'relax.log',
    }

DEFAULT_CALC_CONFIG = {
    'calc_type': None,
    'functional': None,
    'potential_dirname': Essential(),
    'dispersion': None,
    'model': None,
    'modal': None,
    'calc_args': {'device': None},
    }


DEFAULT_DATA_CONFIG = {
    'input': Essential(),
    'load_args': {'index': ':'},
    }


DEFAULT_UNITCELL_CONFIG = {
    'run': True,
    'load': None,
    'write': None,
    'save': None,
    'opt': Essential(),
    }


DEFAULT_DEFORM_CONFIG = {
    'save': None,
    'write': None,
    'opt': Essential(),
    'run': True,
    'load': None,
    'load_opt': None,
    'delta': None,
    'Nsteps': None,
    'e_min': None,
    'e_max': None,
    }

DEFAULT_PHONON_CONFIG = {
    'load': None,
    'save': None,
    'opt': None,
    'primitive': [1,1,1],
    'symprec': None,
    'supercell': [3,3,3],
    'symmetrize': True,
    'distance': None,
    'random_seed': None
    }


DEFAULT_HARMONIC_CONFIG = {
    'save': None,
    'fc2': True,
    'mesh': True,
    'mesh_numbers': [19,19,19],
    'dos': True,
    'band': True,
    'symprec': 1e-05,
    't_min': None,
    't_max': None,
    't_step': None,
    }


DEFAULT_QHA_CONFIG = {
    'save': None,
    'write': None,
    't_max': None,
    'sparse': None,
    'data': None,
    'plot': None,
    'full': None,
    'eos': 'birch-murnahghan',
    }

def overwrite_default(config, argv: list[str] | None=None):
    args = parse_args(argv)
    config['prefix'] =args.prefix
    config['calculator']['calc_type'] =args.calc_type
    config['calculator']['functional'] =args.functional
    config['calculator']['potential_dirname'] =args.potential_dirname

    config['calculator']['dispersion'] =args.dispersion
    config['calculator']['modal'] =args.modal
    config['calculator']['model'] =args.model
    return config

def update_default_config(config):
    key_parse_pair = {
        'data': DEFAULT_DATA_CONFIG,
        'calculator': DEFAULT_CALC_CONFIG,
        'unitcell': DEFAULT_UNITCELL_CONFIG,
        'deform': DEFAULT_DEFORM_CONFIG,
        'phonon': DEFAULT_PHONON_CONFIG,
        'harmonic': DEFAULT_HARMONIC_CONFIG,
        'qha': DEFAULT_QHA_CONFIG,
    }

    for key, default_config in key_parse_pair.items():
        config_parse = default_config.copy()
        config_parse.update(config[key])

        for k, v in config_parse.items():
            if not isinstance(v, Essential):
                continue
            if isinstance(v, Essential):
                if config['calculator']['calc_type'].lower() in ['dft', 'vasp', 'fp']:
                    continue
                else:
                    raise ValueError(f'{key}: {k} must be given')
        config[key] = config_parse
    return config

def _isinstance_in_list(inp, insts):
    return any([isinstance(inp, inst) for inst in insts])

def _islistinstance(inps, insts):
    return all([_isinstance_in_list(inp, insts) for inp in inps])

def check_data_config(config):
    config_data = config['data']
    assert os.path.exists(config_data['input']), 'input dir not found'

def check_unitcell_config(config):
    conf = config['unitcell'].copy()
    os.makedirs(conf['save'], exist_ok = True)
    if (load := conf['load']) is not None:
        assert os.path.exists(load)

def check_deform_config(config):
    conf = config['deform'].copy()
    os.makedirs(conf['save'], exist_ok=True)
    if (load := conf['load']) is not None:
        assert os.path.exists(load)
    assert 0 < conf['delta'] < 1
    assert isinstance(conf['Nsteps'], int)

def check_phonon_config(config):
    conf = config['phonon']
    os.makedirs(conf['save'], exist_ok=True)
    if (load := conf['load']) is not None:
        assert os.path.exists(load)
    assert isinstance(conf['symmetrize'], bool)
    assert isinstance(conf['distance'], float)
    assert _islistinstance(conf['supercell'], [int])
    assert _islistinstance(conf['primitive'], [int]) or isinstance(conf['primitive'], str)

def check_harmonic_config(config):
    conf = config['harmonic']
    os.makedirs(conf['save'], exist_ok=True)
    assert isinstance(conf['fc2'], bool)
    assert isinstance(conf['mesh'], bool)
    assert isinstance(conf['dos'], bool)
    assert isinstance(conf['band'], bool)
    assert isinstance(conf['thermal'], bool)
    assert isinstance(conf['t_min'], (int,float))
    assert isinstance(conf['t_max'], (int,float))
    assert isinstance(conf['t_step'], (int,float))


def check_qha_config(config):
    conf = config['qha']
    assert (eos := conf['eos']) in ['birch', 'vinet', 'birch_murnaghan']
    if conf.get('save', None) is not None:
        os.makedirs(conf['save'], exist_ok = True)
        os.makedirs(f"{conf['save']}/{conf['data']}", exist_ok = True)
        os.makedirs(f"{conf['save']}/{conf['plot']}", exist_ok = True)
        os.makedirs(f"{conf['save']}/{conf['full']}", exist_ok = True)

def update_config_dirs(config):
    prefix = config['prefix']
    config['cwd'] = (cwd := f"./{prefix}")
    os.makedirs(cwd, exist_ok=True)
    os.makedirs('output', exist_ok=True)
    config['output'] = './output'
    tasks = ['unitcell', 'deform', 'phonon', 'harmonic', 'qha']
    for task in tasks:
        if (save_path := config[task].get('save')) is not None:
            config[task]['save'] = f"{cwd}/{save_path}"
        if (load_path := config[task].get('load')) is not None:
            config[task]['load'] = f"{cwd}/{load_path}"
        if (load_path := config[task].get('load_opt')) is not None:
            config[task]['load_opt'] = f"{cwd}/{load_path}"
    return config

def parse_config(config, argv: list[str] | None=None):
    config = update_default_config(config)
    config = overwrite_default(config, argv)
    config = update_config_dirs(config)

    check_data_config(config)
    check_unitcell_config(config)
    check_deform_config(config)
    check_phonon_config(config)
    check_harmonic_config(config)
    check_qha_config(config)

    config = check_calc_config(config)
    config['root'] = os.path.abspath(os.getcwd()) # short stopper
    config['cwd'] = os.path.join(os.path.abspath(os.getcwd()), config['cwd'])
    config['output'] = os.path.join(os.path.abspath(os.getcwd()), config['output'])
    return config

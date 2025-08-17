import os
from cte2.calc.parse_calc_config import check_calc_config
from cte2.util.parse_args import args_parser

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

DEFAULT_DATA_CONFIG = {
    'input': Essential(),
    'load_args': {'index': ':'},
}


DEFAULT_UNITCELL_CONFIG = {
    'run': True,
    'load': None,
    'save': None,
    'opt': Essential()
}


DEFAULT_DEFORM_CONFIG = {
    'save': None,
    'write': 'e-v.csv', 
    'opt': Essential()
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
    'primitive': [1, 1, 1],
    'symprec': None,
    'supercell': [3,3,3], 
    'symmtrize': True,
    'distance': None
    'random_seed': None
}


DEFAULT_HARMONIC_CONFIG = {
    'save': None,
    'fc2': True,
    'mesh': True,
    'mesh_numbers': [19,19,19],
    'dos': True,
    'band': True
    'symprec': 1e-05,
    't_min': None,
    't_max': None,
    't_step': None,
}


DEFAULT_QHA_CONFIG = {
    'save': None,
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
    
    if args.calc_type.lower() in ['vasp', 'dft']:
        config['calculator']['potcar_dirname'] =args.potcar_dirname
    else:
        config['calculator']['dispersion'] =args.dispersion
        config['calculator']['dirname'] =args.dirname
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
        'harmonic': DEFAULT_THERMAL_CONFIG,
        'qha': DEFAULT_QHA_CONFIG,
    }

    for key, default_config in key_parse_pair.items():
        config_parse = default_config.copy()
        config_parse.update(config[key])

        for k, v in config_parse.items():
            if not isinstance(v, Essential):
                continue
            raise ValueError(f'{key}: {k} must be given')
        config[key] = config_parse
    return config

def _isinstance_in_list(inp, insts):
    return any([isinstance(inp, inst) for inst in insts])

def _islistinstance(inps, insts):
    return all([_isinstance_in_list(inp, insts) for inp in inps])

def check_opt_args(calc_conf):
    assert isinstance(calc_conf['fmax'], float), 'fmax must be a float'
    assert isinstance(calc_conf['steps'], (int, float)), 'steps must be a number ... right?'
    assert calc_conf['optimizer'].lower() in ['lbfgs', 'fire', 'fire2']
    assert isinstance((cell_filter:=calc_conf.get('cell_filter', None)), (str, type(None)))
    if cell_filter is not None:
        assert cell_filter.lower() in ['unitcell', 'frechet']
        if (mask := calc_conf.get('mask', None)) is not None:
            assert _islistinstance(mask, [int]), 'mask must be a list if cell_filter is set'
    assert isinstance(calc_conf['fix_symm'], bool)
    assert isinstance(calc_conf['fix_atom'], bool)
    assert isinstance(calc_conf['logfile'], str)

def check_data_config(config):
    config_data = config['data']
    assert os.path.exists(config_data['input']), 'input dir not found'

def check_unitcell_config(config):
    conf = config['unitcell'].copy()
    os.makedirs(conf['save'], exist_ok = True)
    if (load := conf['load']) is not None:
        assert os.path.exists(load)
    check_opt_args(config['opt'][conf['opt']])

def check_deform_config(config):
    conf = config['deform'].copy()
    os.makedirs(conf['save'], exist_ok=True)
    if (load := conf['load']) is not None:
        assert os.path.exists(load)
    assert 0 < conf['delta'] < 1
    assert isinstance(conf['Nsteps'], int)
    check_opt_args(config['opt'][conf['opt']])

def check_phonon_config(config):
    conf = config['phonon']
    os.makedirs(conf['save'], exist_ok=True)
    if (load := conf['load']) is not None:
        assert os.path.exists(load)
    assert isinstance(conf['symmetrize'], bool)
    assert isinstance(conf['distance'], float)
    assert _islistinstance(conf['supercell'], [int])
    assert _islistinstance(conf['primitive'], [int])
 
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
    config = overwrite_default(config, argv)
    config = update_default_config(config)
    config = update_config_dirs(config)

    check_data_config(config)
    check_relax_config(config)
    check_opt_config(config)
    check_deform_config(config)
    check_thermal_config(config)
    check_fc2_config(config)
    check_phonon_config(config)
    check_qha_config(config)

    config = check_calc_config(config)
    config['root'] = os.path.abspath(os.getcwd()) # short stopper
    config['cwd'] = os.path.join(os.path.abspath(os.getcwd()), config['cwd'])
    config['output'] = os.path.join(config['root'], 'output')
    return config

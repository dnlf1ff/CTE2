import os
from cte.utils.

def check_data_config(config):
    config_data = config['data']
    assert os.path.exists(config_data['input']), 'input files not found'

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
    assert isinstance(conf['ratio'], list[float])

def check_supercell_config(config):
    conf = config['supercell']
    os.makedirs(conf['save'], exist_ok=True)
    if (load := conf['load']) is not None:
        assert os.path.exists(load)
    assert isinstance(conf['distance'], float)
    assert _islistinstance(conf['supercell_matrix'], [int])

def check_phonon_config(config):
    conf = config['phonon']
    os.makedirs(conf['save'], exist_ok=True)
    assert isinstance(conf['symmetrize'], bool)
    assert isinstance(conf['run_dos'], bool)
    assert isinstance(conf['run_band'], bool)
    assert isinstance(conf['t_min'], (int,float))
    assert isinstance(conf['t_max'], (int,float))
    assert isinstance(conf['t_step'], (int,float))


def check_qha_config(config):
    conf = config['qha']
    assert (eos := conf['eos']) in ['birch', 'vinet', 'birch_murnaghan']
    assert ('sparse' in conf.keys() or 'thin_number' in conf.keys())
    if conf.get('save', None) is not None:
        os.makedirs(conf['save'], exist_ok = True)
        os.makedirs(f"{conf['save']}/{conf['data']}", exist_ok = True)
        os.makedirs(f"{conf['save']}/{conf['plot']}", exist_ok = True)
        os.makedirs(f"{conf['save']}/{conf['full']}", exist_ok = True)

def update_config_dirs(config):
    os.makedirs(cwd := config['data']['output'], exist_ok=True)

    tasks = ['unitcell', 'deform', 'supercell', 'phonon', 'qha']
    for task in tasks:
        if (save_path := config[task].get('save')) is not None:
            config[task]['save'] = f"{cwd}/{save_path}"
        if (load_path := config[task].get('load')) is not None:
            config[task]['load'] = f"{cwd}/{load_path}"
        if (load_path := config[task].get('load_opt')) is not None:
            config[task]['load_opt'] = f"{cwd}/{load_path}"
    return config

def parse_config(config, argv: list[str] | None=None):
    config = update_config_dirs(config)

    check_data_config(config)
    check_unitcell_config(config)
    check_deform_config(config)
    check_supercell_config(config)
    check_phonon_config(config)
    check_qha_config(config)

    config['unitcell']['primitive'] = get_primitive_matrix(config)

    config = check_calc_config(config)
    return config

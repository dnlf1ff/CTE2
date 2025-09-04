import os
from cte2.util.utils import get_primitive_matrix

def check_data_config(config):
    config_data = config['data']
    assert os.path.exists(config_data['input']), 'input files not found'

def check_unitcell_config(config):
    conf = config['unitcell'].copy()
    if (load := conf['load']) is not None:
        assert os.path.exists(conf['save'])
    os.makedirs(conf['save'], exist_ok = True)

def check_deform_config(config):
    conf = config['deform'].copy()
    if (load := conf['load']) is not None:
        assert os.path.exists(conf['save'])
    os.makedirs(conf['save'], exist_ok=True)

def check_supercell_config(config):
    conf = config['supercell']
    if (load := conf['load']) is not None:
        assert os.path.exists(conf['save'])
    os.makedirs(conf['save'], exist_ok=True)
    assert isinstance(conf['distance'], float)

def check_phonon_config(config):
    conf = config['phonon']
    os.makedirs(conf['save'], exist_ok=True)
    assert isinstance(conf['symm_fc2'], bool)
    assert isinstance(conf['run_dos'], bool)
    assert isinstance(conf['run_band'], bool)
    assert isinstance(conf['t_min'], (int,float))
    assert isinstance(conf['t_max'], (int,float))
    assert isinstance(conf['t_step'], (int,float))


def check_qha_config(config):
    conf = config['qha']
    assert conf['eos'] in ['birch', 'vinet', 'birch_murnaghan']
    assert ('sparse' in conf.keys() or 'thin_number' in conf.keys())
    if conf.get('save', None) is not None:
        os.makedirs(conf['save'], exist_ok = True)
        os.makedirs(f"{conf['save']}/{conf['data']}", exist_ok = True)
        os.makedirs(f"{conf['save']}/{conf['plot']}", exist_ok = True)
        os.makedirs(f"{conf['save']}/{conf['full']}", exist_ok = True)

def update_config_dirs(config):
    os.makedirs(cwd := config['data']['output'], exist_ok=True)
    cwd = config['data']['cwd'] = os.path.abspath(cwd)

    tasks = ['unitcell', 'deform', 'supercell', 'phonon', 'qha']
    for task in tasks:
        if (save_path := config[task].get('save')) is not None:
            config[task]['save'] = f"{cwd}/{save_path}"
        if (load_path := config[task].get('load')) is not None:
            config[task]['load'] = f"{cwd}/{load_path}"
        if (load_path := config[task].get('load_opt')) is not None:
            config[task]['load_opt'] = f"{cwd}/{load_path}"
    return config

def check_calc_config(config):
    conf = config['calculator']
    assert os.path.isfile(conf['model_path'])
    # assert 'modal' in conf['calc_args'].keys() if conf['calc_type'] in omni

def parse_config(config):
    config = update_config_dirs(config)

    check_data_config(config)
    check_calc_config(config)

    check_unitcell_config(config)
    check_deform_config(config)
    check_supercell_config(config)
    check_phonon_config(config)
    check_qha_config(config)

    config['unitcell']['primitive_matrix'] = get_primitive_matrix(config)

    return config

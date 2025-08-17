import os
import warnings

def check_calc_config(config):
    conf = config['calculator']
    calc_types = ['sevennet', '7net', '7net-mf', 'sevennet-mf', 'dpa', 'esen', 'uma', 'orb', 'vasp', 'dft']

    assert conf['calc_type'].lower() in calc_types
    dirname = conf.get('dirname', None)
    model = conf.get('model', None)
    modal = conf.get('modal', None)

    if conf['calc_type'].lower() in ['vasp', 'dft']:
        assert conf['functional'].lower() in ['pbe', 'pbe54', 'pbd52', 'mpa', 'mp', 'omat24']
        dirname = conf.get('potcar_dirname', None)

    assert os.path.exists(dirname), f'directory for potential file {dirname} does not exists'

    if conf['calc_type'].lower() in ['sevennet-mf', '7net-mf']:
        assert os.path.isfile(potential := f'{dirname}/{model}'), f'MLIP potential not found at {potential}'
        config['calculator']['calc_args']['model'] = potential
        assert modal in ['mpa', 'omat24'], 'SevenNet-MF potentials require "modal" as a keyword'
        config['calculator']['calc_args']['modal'] = modal

    elif conf['calc_type'].lower() in ['sevennet', '7net']:
        assert os.path.isfile(potential := f'{dirname}/{model}'), f'MLIP potential not found at {potential}'
        config['calculator']['calc_args']['model'] = potential
        if modal in ['mpa', 'omat24']:
            warnings.warn('SevenNet-0 and SevenNet-omat does not take "modal" as a keyword ...')
            config['calculator']['calc_args']['modal'] = None

    elif conf['calc_type'].lower() == 'dpa':
        from cte2.util.calc_loader import DPA_MODELS, DPA_MODALS 
        model = model.lower()
        assert model in DPA_MODELS.keys(),f'unknown DPA model {model}'
        model = DPA_MODELS[model]
        assert os.path.isfile(potential := f'{dirname}/{model}'), f'MLIP potential not found at {potential}'
        config['calculator']['calc_args']['model'] = potential
        assert modal in DPA_MODALS.keys(), f'unknown DPA modal {modal}'
        config['calculator']['calc_args']['modal'] = DPA_MODALS[modal]

    elif conf['calc_type'].lower() == 'esen':
        from cte2.util.calc_loader import ESEN_MODELS
        model = model.lower()
        assert model in ESEN_MODELS.keys(), f'unknown eSEN model {model}'
        model = ESEN_MODELS[model]
        assert os.path.isfile(potential := f'{dirname}/{model}'), f'MLIP potential not found at {potential}'
        config['calculator']['calc_args']['model'] = potential
 
    elif conf['calc_type'].lower() == 'orb':
        from cte2.util.calc_loader import ORB_MODELS
        model = model.lower()
        assert model in ORB_MODELS.keys(),f'unknown ORB model {model}'
        model = ORB_MODELS[model]
        # assert os.path.isfile(potential := f'{dirname}/{model}'),f'MLIP potential not found at {potential}'
        config['calculator']['calc_args']['model'] = model

    elif conf['calc_type'].lower() == 'uma':
        from cte2.util.calc_loader import UMA_MODELS, UMA_MODALS, UMA_FUNCTIONALS
        model = model.lower()
        if model.endswith('pt'):
            assert model.lower() in UMA_MODELS.values(), f'unknown UMA model {model}'
            potential = f"{dirname}/{model}"
        else:
            assert model.lower() in UMA_MODELS.keys(), f'unknown UMA model {model}'
            potential = f"{dirname}/{UMA_MODELS[model.lower()]}"

        assert modal in UMA_MODALS.keys(), f'unknown UMA modal {modal}'
        assert os.path.isfile(potential), f'MLIP potential not found at {potential}'
   
        if conf['dispersion']:
            if conf.get('functional', None) in UMA_FUNCTIONALS.values():
                functional = config['calculator']['functional']

            elif conf.get('functional', None) in UMA_FUNCTIONALS.keys():
                functional = UMA_FUNCTIONALS[config['calculator']['functional']]

            elif UMA_MODALS[modal] in UMA_FUNCTIONALS.keys():
                functional = UMA_FUNCTIONALS[UMA_MODALS[modal]]

            else:
                raise NotImplementedError

        else:
            functional = config['calculator']['functional']

        config['calculator']['calc_args']['model'] = potential
        config['calculator']['calc_args']['modal'] = conf['modal']
        config['calculator']['calc_args']['functional'] = functional
        config['calculator']['calc_args']['dispersion'] = conf['dispersion']

    else:
        print('smting is wrong ...')
    

    return config


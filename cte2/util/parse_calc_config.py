import os
import warnings

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


def check_calc_config(config):
    conf = config['calculator']
    calc_types = ['sevenn', 'sevennet', '7net', '7net-mf', 'sevennet-mf', 'dpa', 'esen', 'uma', 'orb', 'vasp', 'dft']

    assert conf['calc_type'].lower() in calc_types
    assert os.path.exists(dirname := conf['potential_dirname']), f"Potential directory {conf['potential_dirname']} does not exist"

    model = conf.get('model', None)
    modal = conf.get('modal', None)

    if conf['calc_type'].lower() in ['vasp', 'dft', 'fp', 'abinit', 'qe', 'siesta']:
        assert conf['functional'].lower() in ['pbe', 'pbe54', 'pbd52', 'mpa', 'mp', 'omat24']
        config['calculator']['model'] = conf['calc_type'] #TODO vasp/qe
        config['calculator']['modal'] =  conf['functional']
        print(f"Using {conf['calc_type']} with functional {conf['functional']}")


    elif conf['calc_type'].lower() in ['sevennet-mf', '7net-mf']:
        assert os.path.isfile(potential := f'{dirname}/{model}'), f'MLIP potential not found at {potential}'
        config['calculator']['calc_args']['model'] = potential
        assert modal in ['mpa', 'omat24'], 'SevenNet-MF potentials require "modal" as a keyword'
        config['calculator']['calc_args']['modal'] = modal
        print(f"Using SevenNet-MF with model {model} and modal {modal}")

    elif conf['calc_type'].lower() in ['sevennet', '7net', 'sevenn']:
        assert os.path.isfile(potential := f'{dirname}/{model}'), f'MLIP potential not found at {potential}'
        config['calculator']['calc_args']['model'] = potential
        if modal in ['mpa', 'omat24']:
            warnings.warn('SevenNet-0 and SevenNet-omat does not take "modal" as a keyword ...')
            config['calculator']['calc_args']['modal'] = None
        print(f"Using SevenNet with model {model}")

    elif conf['calc_type'].lower() == 'dpa':
        from cte2.util.calc_loader import DPA_MODELS, DPA_MODALS 
        model = model.lower()
        assert model in DPA_MODELS.keys(),f'unknown DPA model {model}'
        model = DPA_MODELS[model]
        assert os.path.isfile(potential := f'{dirname}/{model}'), f'MLIP potential not found at {potential}'
        config['calculator']['calc_args']['model'] = potential
        assert modal in DPA_MODALS.keys(), f'unknown DPA modal {modal}'
        config['calculator']['calc_args']['modal'] = DPA_MODALS[modal]
        print(f"Using DPA with model {model} and modal {modal}")

    elif conf['calc_type'].lower() == 'esen':
        from cte2.util.calc_loader import ESEN_MODELS
        model = model.lower()
        assert model in ESEN_MODELS.keys(), f'unknown eSEN model {model}'
        model = ESEN_MODELS[model]
        assert os.path.isfile(potential := f'{dirname}/{model}'), f'MLIP potential not found at {potential}'
        config['calculator']['calc_args']['model'] = potential
        print(f"Using eSEN with model {model}")
 
    elif conf['calc_type'].lower() == 'orb':
        from cte2.util.calc_loader import ORB_MODELS
        model = model.lower()
        assert model in ORB_MODELS.keys(),f'unknown ORB model {model}'
        model = ORB_MODELS[model]
        # assert os.path.isfile(potential := f'{dirname}/{model}'),f'MLIP potential not found at {potential}'
        config['calculator']['calc_args']['model'] = model
        print(f"Using ORB with model {model}")

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
        print(f"Using UMA with model {model}, modal {modal} and functional {functional}, dispersion {conf['dispersion']}")

    else:
        raise NotImplementedError(f"Calculator type {conf['calc_type']} not implemented")


    return config


import os, sys
import time
import datetime
from datetime import timedelta
from cte2.cui.cte2_script import _print_cte2, print_time, _print_end, _print_qha
from typing import Any, Dict, List, Optional
import numpy as np

UNITCELL_LOG_KEYS = ['Formula','SPG_num', 'Conv','Length', 'Angle','Natom']
DEFORM_LOG_KEYS = ['Index', 'Strain','SPG_num', 'Conv','Length', 'Angle', 'Energy','Volume']
PHONON_LOG_KEYS = ['Index', 'PM', 'FC2', 'Mesh', 'Im']
COLUMN_PADDING = 2

def print_time():
    """Print current time."""
    print(
        "-------------------------"
        f"[time {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
        "-------------------------"
        )

def _print_end():
    print("...finished running cte2!")

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Recorder:
    def __init__(self, keys, num=None):
        self.keys = keys
        result_dict = {k: '-' for k in keys}
        result_dicts = result_dict.copy()
        if num is not None:
            self.result_dicts = [result_dicts.copy() for _ in range(num)]
        else:
            self.result_dicts = result_dicts.copy()

    def update(self, dct, idx=None):
        np.set_printoptions(formatter={'float':'{: 0.2f}'.format})
        if idx is not None:
            for key in self.keys:
                try:
                    self.result_dicts[idx].update({key: dct[key]})
                except:
                    self.result_dicts[idx].update({key: '-'})
        else:
             for key in self.keys:
                try:
                    self.result_dicts.update({key: dct[key]})
                except:
                    self.result_dicts.update({key: '-'})
        np.set_printoptions()

class Logger(metaclass=Singleton):
    def __init__(self, num=11, filename=None):
        self.filename = filename
        self.init_time = time.time()
        self.num = num

        self.unitcell_recorder = Recorder(UNITCELL_LOG_KEYS)
        self.deform_recorder = Recorder(DEFORM_LOG_KEYS, num=num)
        self.phonon_recorder = Recorder(PHONON_LOG_KEYS, num=num)

        self.handle = open(filename, 'w+', buffering=1)

    def write(self, content: str):
        if self.handle is not None:
            self.handle.write(content)
        else:
           sys.stdout.write(content)

    def writeline(self, line=''):
        content = line + '\n'
        self.write(content)

    def greet(self):
        self.writeline()
        _print_cte2()
        self.writeline()
        self.log_bar()

    def log_config(self, config: Dict[str, Any]):
        print_time()
        key_list = ['calculator', 'data', 'unitcell', 'deform', 'phonon', 'harmonic']
        max_len = max([len(k) for k in key_list])
        self.writeline()
        self.writeline('Configuration for running cte2')
        for k in key_list:
            self.writeline()
            self.writeline(f'---------------- {k} ----------------')
            v = config[k]
            if isinstance(v, dict):
                self.writeline(f'{k:<{max_len}} :')
                for sub_k, sub_v in v.items():
                    self.writeline(f'    {sub_k:<{max_len-2}} : {sub_v}')
            else:
                self.writeline(f'{k:<{max_len}} : {v}')
            self.writeline()
        self.writeline()

    def log_bar(self, size: int = 100):
        self.writeline('-'*size)

    def _make_string_with_space(self, strings, widths):
        final = ''
        for string, width in zip(strings, widths):
            final += f'{string:>{width+COLUMN_PADDING}}'
        return final

    def log_unitcell(self):
        self.writeline()
        print_time()
        unitcell_dict = self.unitcell_recorder.result_dicts
        max_len_dict = {k: [len(f'{v}')] for k, v in unitcell_dict.items()}
        for key in UNITCELL_LOG_KEYS:
            v = unitcell_dict[key]
            unitcell_dict[key] = f'{v}' # cnv to str
            max_len_dict[key].append(len(f'{v}'))

        max_len_dict = {k: max(max(v), len(k)) for k, v in max_len_dict.items()}
        widths = [max_len_dict[key] for key in UNITCELL_LOG_KEYS]
        bar_len = COLUMN_PADDING*(len(UNITCELL_LOG_KEYS)+1) + sum(max_len_dict.values())

        self.log_bar(bar_len)
        self.writeline(self._make_string_with_space(UNITCELL_LOG_KEYS, widths))
        self.log_bar(bar_len)
        strings = [unitcell_dict[key] for key in UNITCELL_LOG_KEYS]
        self.writeline(self._make_string_with_space(strings, widths))
        self.log_bar(bar_len)
        self.writeline()

    def log_deform(self):
        self.writeline()
        print_time()
        deform_dicts = self.deform_recorder.result_dicts
        max_len_dict = {k: [len(f'{v}')] for k, v in deform_dicts[0].items()}
        for idx, deform_dict in enumerate(deform_dicts):
            deform_dict['Index'] = idx
            if idx == 0:
                max_len_dict = {k: [] for k in deform_dict.keys()}

            for key in DEFORM_LOG_KEYS:
                v = deform_dict[key]
                deform_dict[key] = f'{v}' # cnv to str
                max_len_dict[key].append(len(f'{v}'))

        max_len_dict = {k: max(max(v), len(k)) for k, v in max_len_dict.items()}
        widths = [max_len_dict[key] for key in DEFORM_LOG_KEYS]
        bar_len = COLUMN_PADDING*(len(DEFORM_LOG_KEYS)+1) + sum(max_len_dict.values())

        self.log_bar(bar_len)
        self.writeline(self._make_string_with_space(DEFORM_LOG_KEYS, widths))
        for idx, deform_dict in enumerate(deform_dicts):
            if idx==0:
                self.log_bar(bar_len)
            strings = [deform_dict[key] for key in DEFORM_LOG_KEYS]
            self.writeline(self._make_string_with_space(strings, widths))
        self.log_bar(bar_len)
        self.writeline()

    def log_phonon(self):
        self.writeline()
        print_time()
        phonon_dicts = self.phonon_recorder.result_dicts
        max_len_dict = {k: [len(f'{v}')] for k, v in phonon_dicts[0].items()}
        for idx, phonon_dict in enumerate(phonon_dicts):
            phonon_dict['Index'] = idx
            if idx == 0:
                max_len_dict = {k: [] for k in phonon_dict.keys()}

            for key in PHONON_LOG_KEYS:
                v = phonon_dict[key]
                phonon_dict[key] = f'{v}' # cnv to str
                max_len_dict[key].append(len(f'{v}'))

        max_len_dict = {k: max(max(v), len(k)) for k, v in max_len_dict.items()}
        widths = [max_len_dict[key] for key in PHONON_LOG_KEYS]
        bar_len = COLUMN_PADDING*(len(PHONON_LOG_KEYS)+1) + sum(max_len_dict.values())

        self.log_bar(bar_len)
        self.writeline(self._make_string_with_space(PHONON_LOG_KEYS, widths))
        for idx, phonon_dict in enumerate(phonon_dicts):
            if idx==0:
                self.log_bar(bar_len)
            strings = [phonon_dict[key] for key in PHONON_LOG_KEYS]
            self.writeline(self._make_string_with_space(strings, widths))
        self.log_bar(bar_len)
        self.writeline()


    def terminate(self):
        total = time.time() - self.init_time
        self.writeline(f'Total elapsed time: {timedelta(seconds=total)}')
        self.writeline('cte2 terminated.')
        print_time()
        self.handle.close()
        self.handle = None


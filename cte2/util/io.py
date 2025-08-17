import yaml
import os
from typing import Any, Optional, Union

def dict_representer(dumper, data=None):
    return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data, flow_style=False)
def list_representer(dumper, data=None):
    return dumper.represent_sequence(yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, data, flow_style=True)

class WDumper(yaml.Dumper):
    def write_line_break(self, data=None):
        super().write_line_break(data)
        if len(self.indents) == 1:
            super().write_line_break()

def dumpYAML(data, filename, indent=4, sort_keys=False, explicit_start=True, explicit_end=True, default_flow_style=False,):
    yaml.add_representer(dict, dict_representer, Dumper=WDumper)
    yaml.add_representer(list, list_representer, Dumper=WDumper)
    with open(filename, 'w') as fp:
        yaml.dump(data, fp, Dumper=WDumper, sort_keys=sort_keys, explicit_start=explicit_start, explicit_end=explicit_end, default_flow_style=default_flow_style, indent=indent)


def DatToCsv(inp: Union[str, os.PathLike], out: Union[str, os.PathLike], columns: Optional[str]=None) -> None:
    """
    ----------------

    Parameters
    ----------------
    inp: str|os.PathLike
        dir of the input .dat file

    out: str|os.PathLike
        dir of the output .csv file 

    columns: Optional[str]
        the columns of the output csv file
        something like 'temperature,cte'
        don't forget to remove all whitespaces

    Returns:
    ----------------
    Nothing 
    ...
    
    """

    inp_dat = open(inp, 'r')
    out = open(out, 'w', buffering=1)
    dat_lines = inp_dat.readlines()
    if columns is not None:
        out.writelines(f'{columns}\n')
    for line_number, dat_line in enumerate(dat_lines):
        if '#' in dat_line:
            continue
        try:
            col1=dat_line.split()[0]
            col2=eval(dat_line.split()[1])
            out.write(f'{col1},{col2}\n')
        except Exception as e:
            print('ERROR')
            print(e)
            continue
    inp_dat.close()
    out.close()



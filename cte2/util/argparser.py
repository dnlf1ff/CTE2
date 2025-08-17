import argparse
from types import SimpleNamespace

def base_parser(argv: list[str] | None=None):
    parser = argparse.ArgumentParser(description = "cli tool")

    parser.add_argument('--calc_type', type=str, default='sevennet-mf',
                        help='sevennet,sevennet-mf, esen, uma, vasp')
 
    parser.add_argument('--config', type=str, default='./config.yaml', help='config yaml file directory')
 
    parser.add_argument('--prefix', '--prefix', dest='cwd', type=str, default='vasp', help='working directory')

    parser.add_argument('--functional', type=str, default='PBE54', help='VASP pseudo-potential functional')

    return parser.parse_args(argv)

def vasp_parser(argv: list[str] | None=None):
    parser = argparse.ArgumentParser(description = "cli tool for VASP")
    parser.add_argument('--potcar_dirname', default='.', type=str, help='dir for potcar files')

    parser.add_argument('--task', default='unitcell', type=str, help='task to run')

    return parser.parse_args(argv)

def mlip_parser(argv: list[str] | None=None):

    parser = argparse.ArgumentParser(description = "cli tool for U-MLIP")
 
    parser.add_argument('--model', dest='model', type=str, default='.',
                        help='absolute directory of the U-MLIP potential')

    parser.add_argument('--model_dirname','--model_path','--path','--dirname', dest='dirname',type=str, default='.',
                        help='absolute directory of the U-MLIP potential')

    parser.add_argument('--modal','--task', '--head','--task_name', dest='modal', type=str, 
                        default='omat24',help='data modality for multi-functional U-MLIPs; mpa, omat24 etc.')

    parser.add_argument('--dispersion', type=bool, 
                        default=False, help='whether to exclude D3')

    return parser.parse_args(argv)

def merge_args(*args):
    merged = SimpleNamespace()
    for arg in  args:
        for key, value in vars(arg).items():
            setattr(merged, key, value)
    return merged

def parse_args(argv: list[str] | None=None):
    base_args = base_parser(argv)
    if base_args.calc_type.lower() == 'vasp':
        args = vasp_parser(argv)
        args = merge_args(base_args, args)
    else:
        args = mlip_parser(argv)
        args = merge_args(base_args, args)
    return args


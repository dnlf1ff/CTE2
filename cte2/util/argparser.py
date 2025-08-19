import argparse
from types import SimpleNamespace

def parse_args(argv: list[str] | None=None):
    parser = argparse.ArgumentParser(description = "cli tool")

    parser.add_argument('--calc_type', type=str, default='sevennet-mf',
                        help='sevennet,sevennet-mf, esen, uma, vasp')
 
    parser.add_argument('--config', type=str, default='./config.yaml', help='config yaml file directory')
 
    parser.add_argument('--prefix', '--cwd', dest='prefix', type=str, default='vasp', help='working directory')

    parser.add_argument('--potential_dirname', default='.', type=str, help='dir for potcar files')

    parser.add_argument('--functional', type=str, default='PBE54', help='VASP pseudo-potential functional')


    parser.add_argument('--model', dest='model', type=str, default='.',
                        help='absolute directory of the U-MLIP potential')

    parser.add_argument('--modal', '--head', dest='modal', type=str,
                        default='omat24',help='data modality for multi-functional U-MLIPs; mpa, omat24 etc.')

    parser.add_argument('--task', '--vasp_task', dest='task', type=str,
                        default='harmonic',help='data modality for multi-functional U-MLIPs; mpa, omat24 etc.')


    parser.add_argument('--dispersion', type=bool,
                        default=False, help='whether to exclude D3')

    return parser.parse_args(argv)


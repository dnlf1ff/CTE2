import sys, yaml, gc
from cte2.util.calc import calc_from_config

from cte2.util.argparser import parse_args
from cte2.util.config import parse_config
from cte2.util.logger import Logger
from cte2.util.io import dumpYAML

from cte2.mlip.preprocess import process_input, process_deform
from cte2.mlip.postprocess import process_phonon

import torch
import warnings

def main(argv: list[str] | None=None) -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="seekpath.hpkot")
    args = parse_args(argv)
    config_dir = args.config

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config = parse_config(config, argv)
    dumpYAML(config, f'{config["dir"]["cwd"]}/config_mlip.yaml')

    logger = Logger(filename=f"{config['dir']['cwd']}/{config['dir']['prefix']}_cte2.log", num=config['deform']['Nsteps'],)
    logger.greet()

    logger.writeline('Reading config successful!')
    logger.log_config(config)

    calc = calc_from_config(config)

    if args.task in ['unitcell']:
        process_input(config, calc)
        logger.log_unitcell()

    if args.task in ['deform', 'deformation', 'elastic', 'elasticity']:
        process_deform(config, calc)
        logger.log_deform()

    if args.task in ['post', 'postprocess']:
        process_phonon(config)

    if args.task in ['fc2', 'fc', 'force_constants']:
        from cte2.cte.fc2 import process_fc2
        process_fc2(config, calc)

    if args.task in ['harmonic', 'dos', 'band', 'thermal']:
        from cte2.cte.harmonic import process_harmonic
        process_harmonic(config, calc)
        logger.log_phonon()

    if args.task in ['qha']:
        from cte2.cte.qha import process_qha
        process_qha(config, calc)

    if args.task in ['all']:
        process_input(config, calc)
        logger.log_unitcell()
        process_deform(config, calc)
        logger.log_deform()
        process_phonon(config)

        from cte2.cte.fc2 import process_fc2
        process_fc2(config, calc)

        from cte2.cte.harmonic import process_harmonic
        process_harmonic(config)
        logger.log_phonon()

        from cte2.cte.qha import process_qha
        process_qha(config, calc)

if __name__ == '__main__':
    main()

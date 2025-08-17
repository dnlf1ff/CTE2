import sys, yaml, gc
from cte2.util.argparser import parse_args
from cte2.util.config import parse_config

from cte2.cte.fc2 import process_fc2
from cte2.cte.harmonic import process_harmonic
from cte2.cte.qha import process_qha

import pandas as pd
import torch
import warnings

def main(argv: list[str] | None=None) -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="seekpath.hpkot")
    args = parse_args(argv)

    config_dir = cte2_args.config

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config = parse_config(config, argv)
    dumpYAML(config, f'{config["cwd"]}/config.yaml')

    logger = Logger(num = config["deform"]["Nsteps"], f"{config['output']}/{prefix}_cte2.log")
    logger.greet()

    logger.writeline('Reading config successful!')
    logger.log_config(config)

    if args.calc_type.lower() in ['vasp', 'dft']:
        from cte2.vasp.preprocess as process_input, process_deform
        from cte2.vasp.postprocess as process_phonon, post_unitcell, post_deform

        if args.task.lower() == 'unitcell':
            process_input(config)

        if args.task.lower() in ['deform', 'deformed', 'strain', 'strained']:
            process_deform(config)

        if args.task.lower() in ['phonon', 'static']:
            process_phonon(config)

        post_unitcell(config)
        post_deform(config)
        logger.log_unitcell()
        logger.log_deform()
        process_fc2(config)

    else:
        from cte2.mlip.preprocess as process_input, process_deform
        calc = calc_from_config(config)
        process_input(config, calc)
        logger.log_unitcell()

        process_deform(config, calc)
        logger.log_deform()
        process_fc2(config, config)

    process_harmonic(config)
    logger.log_phonon()

    if config['qha']['run']:
        process_qha(config)

if __name__ == '__main__':
    main()

import sys, yaml, gc
from cte2.util.calc import calc_from_config

from cte2.util.argparser import parse_args
from cte2.util.config import parse_config
from cte2.util.logger import Logger
from cte2.util.io import dumpYAML

from cte2.mlip.preprocess import process_input, process_deform

import torch
import warnings

def main(argv: list[str] | None=None) -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="seekpath.hpkot")
    args = parse_args(argv)
    config_dir = args.config

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config = parse_config(config, argv)
    dumpYAML(config, f'{config["cwd"]}/config.yaml')

    logger = Logger(f"{config['prefix']}_cte2.log")
    logger.greet()

    logger.writeline('Reading config successful!')
    logger.log_config(config)

    calc = calc_from_config(config)

    process_input(config, calc)
    logger.log_unitcell()

    process_deform(config, calc)
    logger.log_deform()

if __name__ == '__main__':
    main()

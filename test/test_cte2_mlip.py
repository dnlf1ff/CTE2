import sys, yaml, gc
from cte2.test.util.test_calc import calc_from_config

from cte2.util.test_argparser import parse_args
from cte2.test.util.test_config import parse_config
from cte2.util.logger import Logger

from cte2.mlip.preprocess as process_input, process_deform
from cte2.mlip.postprocess as process_phonon

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

    logger = Logger(f"{config['output']}/{prefix}_cte2.log")
    logger.greet()

    logger.writeline('Reading config successful!')
    logger.log_config(config)

    calc = calc_from_config(config)

    process_input(config, calc)
    logger.log_unitcell()

    process_deform(config, calc)
    logger.log_deform()

    process_phonon(config)
    logger.log_phonon()


if __name__ == '__main__':
    main()

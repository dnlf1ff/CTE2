from cte2.util.logger import Logger
from cte2.util.argparser import parse_args
from cte2.util.config import parse_config
from cte2.util.io import dumpYAML
from cte2.util.calc import calc_from_config
from cte2.cte.fc2 import process_fc2

import os, sys, yaml

def main(argv: list[str]|None=None) -> None:
    args = parse_args(argv)
    config_dir = args.config 

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
   
    config = parse_config(config)
    logger = Logger(filename=f"{config['dir']['cwd']}/fc2.log", num = config['deform']['Nsteps'])
    logger.log_config(config)
    dumpYAML(config, f"{config['dir']['cwd']}/config_fc2.yaml")

    calc = calc_from_config(config)

    process_fc2(config, calc=calc)

if __name__ == '__main__':
    main()

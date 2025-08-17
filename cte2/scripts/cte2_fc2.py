from cte2.util.logger import Logger
from cte2.util.argparser import parse_args
from cte2.util.config import parse_config
from cte2.util.io import dumpYAML
from cte2.util.calc import calc_from_config
from cte2.cte.fc2 import process_fc2

import yaml
import sys

def main(argv: list[str]|None=None) -> None:
    args = parse_args(argv)
    config_dir = args.config 

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
   
    config = parse_config(config)
    logger = Logger(filename=f"{config['cwd']}/fc2.log", num = config['deform']['Nsteps'])
    logger.log_config(config)
    dumpYAML(config, f"{config['cwd']}/config_fc2.yaml")

    calc = calc_from_config(config)

    try:
        process_fc2(config, calc=calc)

    except Exception as e:
        if calc is None:
            from cte2.vasp.postprocess import post_unitcell, post_deform
            post_unitcell(config)
            post_deform(config)
            logger.log_unitcell()
            logger.log_deform()
        else:
            sys.stderr.write(f"Error during calculation: {e}\n")
            sys.exit(1)

if __name__ == '__main__':
    main()

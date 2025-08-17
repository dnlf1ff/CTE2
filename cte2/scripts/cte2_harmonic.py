from cte2.util.logger import Logger
from cte2.util.argparser import parse_args
from cte2.util.config import parse_config
from cte2.util.io import dumpYAML
from cte2.cte.harmonic import process_harmonic

import yaml

def main(argv: list[str]|None=None) -> None:
    args = parse_args(argv)
    config_dir = args.config
    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
   
    config = parse_config(config)
    logger = Logger(filename=f"{config['cwd']}/har.log", num = config['deform']['Nsteps'])
    logger.log_config(config)
    dumpYAML(config, f"{config['cwd']}/config_har.yaml")

    process_harmonic(config)
    logger.log_phonon()

if __name__ == '__main__':
    main()

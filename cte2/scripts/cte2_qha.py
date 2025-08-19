from cte2.util.argparser import parse_args
from cte2.util.config import parse_config
from cte2.util.logger import Logger
from cte2.cte.qha import process_qha
from cte2.util.io import dumpYAML
from cte2.util.calc import calc_from_config
import yaml

def main(argv: list[str] | None=None) -> None:
    args = parse_args(argv)
    config_dir = args.config 

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
   
    config = parse_config(config, argv)
    logger = Logger(filename=f"{config['dir']['cwd']}/qha.log", num = config['deform']['Nsteps'])
    logger.log_config(config)
    dumpYAML(config, f"{config['dir']['cwd']}/config_qha.yaml")


    calc = calc_from_config(config)
    process_qha(config, calc=calc)

if __name__ == '__main__':
    main()

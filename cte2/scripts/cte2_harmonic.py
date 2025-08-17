from cte2.util.logger import Logger
from cte2.cui.argparser import parse_args
from cte2.cui.config import parse_config
from cte2.cte.harmonic import process_harmonic

def main(argv: list[str]|None=None) -> None:
    args = vasp_parsers(argv)
    config_dir = args.config 

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
   
    config = parse_config_yaml(config)
    process_harmonic(config)
    logger.log_phonon()

if __name__ == '__main__':
    main()

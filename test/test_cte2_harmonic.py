from cte2.util.logger import Logger
from cte2.test.util.test_argparser import parse_args
from cte2.test.util.test_config import parse_config
from cte2.cte.harmonic import process_harmonic

def main(argv: list[str]|None=None) -> None:
    args = vasp_parsers(argv)
    config_dir = args.config 

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
   
    config = parse_config_yaml(config)
    logger = Logger(num = config["deform"]["Nsteps"], f"{config['output']}/{prefix}_cte2.log")
    logger.greet()

    logger.writeline('Reading config successful!')
    logger.log_config(config)


    process_harmonic(config)
    logger.log_phonon()

if __name__ == '__main__':
    main()

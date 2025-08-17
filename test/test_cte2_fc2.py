from cte2.util.logger import Logger
from cte2.cte.fc2 import process_fc2
from cte2.util.calc import calc_from_config

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

    if args.calc_type.lower() in ['vasp', 'dft']:
        calc = None
    else:
        calc = calc_from_config(config)

    process_fc2(config, calc)

if __name__ == '__main__':
    main()

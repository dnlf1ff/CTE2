from cte2.util.logger import Logger
from cte2.vasp.preprocess import process_input, process_deform, process_phonon
from cte2.util.argparser import parse_args
from cte2.util.config import parse_config


def main(argv: list[str] | None=None) -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="seekpath.hpkot")
    args = parse_args(argv)

    config_dir = args.config

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config = parse_config(config, argv)
    dumpYAML(config, f'{config["cwd"]}/config.yaml')

    logger = Logger(f"{config['output']}/{prefix}_cte2.log")
    logger.greet()

    logger.writeline('Reading config successful!')
    logger.log_config(config)

    if args.task.lower() == 'unitcell':
        process_input(config)

    if args.task.lower() in ['deform', 'deformed', 'strain', 'strained']:
        process_deform(config)

    if args.task.lower() in ['phonon', 'static']:
        process_deform(config)



if __name__ == '__main__':
    main()

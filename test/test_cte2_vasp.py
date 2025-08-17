from cte2.util.logger import Logger
from cte2.vasp.preprocess import process_input, process_deform, process_phonon
from cte2.test.util.test_argparser import parse_args
from cte2.test.util.test_config import parse_config
from cte2.vasp.postprocess as process_phonon, post_unitcell, post_deform

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
        post_unitcell(config)
        logger.log_unitcell()

    if args.task.lower() in ['phonon', 'static']:
        process_phonon(config)
        post_deform(config)
        logger.log_deform()



if __name__ == '__main__':
    main()

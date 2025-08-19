from cte2.util.logger import Logger
from cte2.vasp.preprocess import process_input, process_deform, process_phonon
from cte2.util.argparser import parse_args
from cte2.util.config import parse_config
from cte2.util.io import dumpYAML

import yaml, warnings

def main(argv: list[str] | None=None) -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="seekpath.hpkot")
    args = parse_args(argv)

    config_dir = args.config

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config = parse_config(config, argv)
    dumpYAML(config, f'{config["dir"]["cwd"]}/config_vasp.yaml')

    logger = Logger(num = config['deform']['Nsteps'], filename=f"{config['dir']['cwd']}/cte2.log")
    logger.greet()

    logger.writeline('Reading config successful!')
    logger.log_config(config)

    if args.task.lower() == 'unitcell':
        process_input(config)

    if args.task.lower() in ['deform', 'deformed', 'strain', 'strained']:
        process_deform(config)

    if args.task.lower() in ['phonon', 'static']:
        process_phonon(config)

    if args.task.lower() in ['post', 'postprocess', 'post-processing']:
        from cte2.vasp.postprocess import post_unitcell, post_deform
        post_unitcell(config)
        post_deform(config)

    if args.task.lower() == 'all':
        process_input(config)
        process_deform(config)
        process_phonon(config)
        from cte2.vasp.postprocess import post_unitcell, post_deform
        from cte2.cte.fc2 import process_fc2
        from cte2.cte.harmonic import process_harmonic
        from cte2.cte.qha import process_qha
        post_unitcell(config)
        post_deform(config)
        process_fc2(config)
        process_harmonic(config)
        process_qha(config)




if __name__ == '__main__':
    main()

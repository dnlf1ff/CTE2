from cte2.util.logger import Logger
from cte2.cui.argparser import parse_args
from cte2.cui.config import parse_config
from cte2.cte.fc2 import process_fc2

def main(argv: list[str]|None=None) -> None:
    args = vasp_parsers(argv)
    config_dir = args.config 

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
   
    config = parse_config_yaml(config)
    process_fc2(config)

    if args.calc_type.lower() in ['vasp', 'dft']:
        from cte2.vasp.postprocess as process_phonon, post_unitcell, post_deform
        post_unitcell(config)
        post_deform(config)
        process_fc2(config)
    else:
        calc = calc_from_config(config)
        process_fc2(config, config)

if __name__ == '__main__':
    main()

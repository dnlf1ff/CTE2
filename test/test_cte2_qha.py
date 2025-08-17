from cte2.test.util.test_argparser import parse_args
from cte2.test.util.test_config import parse_config
from cte2.cte.qha import process_qha
from cte2.util.calc import calc_from_config


def main(argv: list[str] | None=None) -> None:
    args = parse_args(argv)
    config_dir = args.config 

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
   
    config = parse_config(config)
    if args.calc_type.lower() in ['vasp', 'dft', 'fp']:
        calc = None
    else:
        calc = calc_from_config(config)

 
    process_qha(config)


if __name__ == '__main__':
    main()

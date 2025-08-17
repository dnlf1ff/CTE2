from cte2.cui.argparser import parse_args
from cte2.cui.config import parse_config
from cte2.cte.qha import process_qha


def main(argv: list[str] | None=None) -> None:
    args = parse_args(argv)
    config_dir = args.config 

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
   
    config = parse_config(config)
    process_qha(config)


if __name__ == '__main__':
    main()

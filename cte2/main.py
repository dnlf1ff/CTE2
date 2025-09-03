import sys, yaml, gc

from cte2.util.config import parse_config
from cte2.util.io import dumpYAML
from cte2.util.calc import get_calc

from cte2.structure.unitcell import process_unitcell
from cte2.structure.deform import process_deform
from cte2.structure.supercell import process_supercell

from cte2.phonon.fc2 import process_fc2
from cte2.phonon.harmonic import process_harmonic
from cte2.phonon.qha import process_qha


def main(argv: list[str] | None=None) -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="seekpath.hpkot")
    args = parse_args(argv)
    config_dir = args.config

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config = parse_config(config, argv)
    dumpYAML(config, f'{config["data"]["cwd"]}/config_mlip.yaml')

    calc = calc_from_config(config)

    process_input(config, calc)
        
    process_deform(config, calc)

    process_phonon(config)

    process_fc2(config, calc)

    process_harmonic(config)

    process_qha(config, calc)

if __name__ == '__main__':
    main()

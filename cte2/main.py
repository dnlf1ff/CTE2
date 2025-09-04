import warnings, sys
import yaml

from cte2.util.parser import parse_config
from cte2.util.io import dumpYAML
from cte2.util.calc import get_calc

from cte2.structure.unitcell import process_unitcell
from cte2.structure.deform import process_deform
from cte2.structure.supercell import process_supercell

from cte2.phonon.fc2 import process_fc2
from cte2.phonon.harmonic import process_harmonic
from cte2.phonon.qha import process_qha

 
def main(config_dir=None):
    if config_dir is None:
        config_dir = sys.argv[1]

    warnings.filterwarnings("ignore", category=DeprecationWarning, module="seekpath.hpkot")

    with open(config_dir, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config = parse_config(config)
    dumpYAML(config, f'{config["data"]["cwd"]}/config_parsed.yaml')

    calc = get_calc(config)

    if config['unitcell']['run']:
        process_unitcell(config, calc)
        
    if config['deform']['run']:
        process_deform(config, calc)

    if config['supercell']['run']:
        process_supercell(config)

    process_fc2(config, calc)

    process_harmonic(config)

    process_qha(config, calc)

if __name__ == '__main__':
    config_dir = sys.argv[1]
    main(config_dir)

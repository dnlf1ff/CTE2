from ase.io import read
from pymatgen.io.vasp.sets import MPRelaxSet
from pymatgen.io.vasp import Potcar, Poscar, Incar, Kpoints
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.core import Structure
import numpy as np

class Essential:
    pass

INCAR_UNITCELL = {
        'PREC': 'Accurate',
        'IBRION': 2,
        'NSW': 20,
        'NELMIN': 5,
        'ISIF': 3,
        'ENCUT': 520,  # 500 for metal
        'EDIFF': 1e-08,
        'EDIFFG': -1e-08,
        'ISMEAR': 0,  # 1 for metals
        'SIGMA': 1e-02,
        'ALGO': 'Normal',
        'LREAL': False,
        'ADDGRID': True,
        'LWAVE': False,
        'LCHARG': False,
        'NPAR': 4
    }

INCAR_DEFORMED = {
        'PREC': 'Accurate',
        'IBRION': 2,
        'NSW': 20,
        'NELMIN': 5,
        'ISIF': 2,
        'ENCUT': 520,  # 500 for metal
        'EDIFF': 1e-08,
        'EDIFFG': -1e-08,
        'ISMEAR': 0,  # 1 for metals
        'SIGMA': 1e-02,
        'ALGO': 'Normal',
        'LREAL': False,
        'ADDGRID': True,
        'LWAVE': False,
        'LCHARG': False,
        'NPAR': 4
    }


KPOINTS_RELAX = {
        'comment': 'Kpoints for unitcell relaxation',
        'nkpoints': 0,
        'generation_style': 'Monkhorst-pack',
        'kpoints': [3, 3, 3],
        'usershift': [0, 0, 0]
    }

INCAR_FORCE = {
        'PREC': 'Accurate',
        'IBRION': -1,
        'NELMIN': 5,
        'ENCUT': 520,  # 500 for metal
        'EDIFF': 1e-08,
        'ISMEAR': 0,  # 1 for metals
        'SIGMA': 1e-02,
        'ALGO': 'Normal',
        'LREAL': False,
        'ADDGRID': True,
        'LWAVE': False,
        'LCHARG': False,
        'NPAR': 4
    }

KPOINTS_FORCE = {
        'comment': 'Kpoints for supercell force calculation',
        'nkpoints': 0,
        'generation_style': 'Monkhorst-pack',
        'kpoints': [3, 3, 3],
        'usershift': [0, 0, 0]
    }

def write_incar(incar_dict, subdir):
    incar = Incar.from_dict(incar_dict)
    if incar['IBRION'] == -1:
        incar.pop('NSW', None)
        incar.pop('EDIFFG', None)
        incar.pop('ISIF', None)

    incar.write_file(f'{subdir}/INCAR')

def write_kpoints(r_dict, subdir):
    incar = Incar.from_dict(incar_dict)
    incar.write_file(f'{subdir}/INCAR')

def write_potcar(poscar, potcar_config, subdir, POTCAR_DIR):
    elements=poscar.site_symbols
    full_potcar=[]
    for el in elements:
        potcar_name_local=potcar_config[el]
        if el == 'Yb':
            potcar_name_local = 'Yb_3'
        if el == 'W':
            potcar_name_local = 'W_sv'
        potcar_path = POTCAR_PREFIX +'/'+ potcar_name_local + '/'+ "POTCAR"
        with open(potcar_path, "r") as f:
            data = f.readlines()
        full_potcar.extend(data)
    potcar_file = f"{subdir}/POTCAR"
    with open(potcar_file,"w") as f:
        f.write("".join(full_potcar))

def write_mpr_potcar(poscar_dir, subdir, POTCAR_DIR):
    atoms = read(poscar_dir)
    structure=AseAtomsAdaptor.get_structure(atoms)
    config= MPRelaxSet(structure)
    write_potcar(config.poscar, config.CONFIG["POTCAR"], POTCAR_PREFIX=POTCAR_PREFIX, subdir=subdir)

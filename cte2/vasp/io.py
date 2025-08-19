from ase.io import read
from ase import Atoms
import os
from pymatgen.io.vasp.sets import MPRelaxSet
from pymatgen.io.vasp import Potcar, Poscar, Incar, Kpoints
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.core import Structure
import numpy as np

from typing import Union, Dict

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

def write_incar(incar_dct, subdir: Union[str, os.PathLike]):
    incar = Incar.from_dict(incar_dct)
    if incar['IBRION'] == -1:
        incar.pop('NSW', None)
        incar.pop('EDIFFG', None)
        incar.pop('ISIF', None)

    incar.write_file(f'{subdir}/INCAR')

def write_kpoints(kpoints_dct, subdir: Union[str, os.PathLike]):
    kpoints = Kpoints.from_dict(kpoints_dct)
    kpoints.write_file(f'{subdir}/KPOINTS')

def write_potcar(potcar_config, poscar: Poscar, POTCAR_DIR: Union[str, os.PathLike], subdir: Union[str, os.PathLike]):
    elements=poscar.site_symbols
    full_potcar=[]
    for el in elements:
        potcar_name_local=potcar_config[el]
        if el == 'Yb':
            potcar_name_local = 'Yb_3'
        if el == 'W':
            potcar_name_local = 'W_sv'
        potcar_path = f"{POTCAR_DIR}/{potcar_name_local}/POTCAR"
        with open(potcar_path, "r") as f:
            data = f.readlines()
        full_potcar.extend(data)
    potcar_file = f"{subdir}/POTCAR"
    with open(potcar_file,"w") as f:
        f.write("".join(full_potcar))

def write_mpr_potcar(poscar_dir: Union[str, os.PathLike], subdir: Union[str, os.PathLike], POTCAR_DIR: Union[str, os.PathLike]):
    atoms = read(poscar_dir, format='vasp')
    structure=AseAtomsAdaptor.get_structure(atoms)
    config= MPRelaxSet(structure)
    write_potcar(potcar_config=config.CONFIG["POTCAR"], poscar=config.poscar, POTCAR_DIR=POTCAR_DIR, subdir=subdir)

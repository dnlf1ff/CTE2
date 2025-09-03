import numpy as np
import math
import warnings
import seekpath
from ase.io import write

import ase.io as ase_IO
from ase import Atoms
from ase.cell import Cell
from pymatgen.io.vasp import Vasprun
from pymatgen.core import Structure, Lattice

import spglib
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
from phonopy.interface.vasp import write_supercells_with_displacements

PRIMITIVE_MAP = {
        'a': [[1, 0, 0],[0, 0.5, -0.5],[0, 0.5, 0.5]],
        'b': [[0.5, 0, -0.5], [0,1,0], [0.5, 0, 0.5]],
        'c': [[0.5, 0.5, 0], [-0.5, 0.5, 0], [0, 0, 1]],
        'f': [[0, 0.5, 0.5],[0.5, 0, 0.5],[0.5, 0.5, 0]],
        'i': [[-0.5, 0.5, 0.5],[0.5, -0.5, 0.5],[0.5, 0.5, -0.5]],
        'r': [[2/3, -1/3, -1/3], [1/3, 1/3, -2/3], [1/3, 1/3, 1/3]],
        'p': [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 
        }

def write_csv(file, atoms, idx='pre', dlm=','):
    if isinstance(atoms, Atoms):
        dct = atoms.info.copy()
        volume=atoms.get_volume()
        a,b,c = atoms.get_cell().copy().lengths()
        alpha, beta, gamma = atoms.get_cell().copy().angles()
        try:
            conv = dct['conv']
        except:
            conv = '-'
        vals = [idx,dct['e_fr_energy'],volume,len(atoms),a,b,c,alpha,beta,gamma,conv] 
        file.write(f"{dlm}".join(map(str, vals)) + '\n')

    elif isinstance(atoms, Vasprun):
        if 'pre' in idx:
            dct = atoms.ionic_steps[0]
            struct = dct['structure']
            conv = '-'
            natoms = len(struct.sites)
            volume = struct.lattice.volume
            a,b,c = struct.lattice.lengths
            alpha, beta, gamma = struct.lattice.angles
        else:
            dct = atoms.ionic_steps[-1]
            struct = dct['structure']
            conv = atoms.converged
            natoms = len(struct.sites)
            volume = struct.lattice.volume
            a,b,c = struct.lattice.lengths
            alpha, beta, gamma = struct.lattice.angles

        vals = [idx,dct['e_fr_energy'],volume,natoms,a,b,c,alpha,beta,gamma,conv]
        file.write(f"{dlm}".join(map(str, vals)) + '\n')
    else:
        print(atoms)
        print('tlqkf')
        raise TypeError("Unsupported type for atoms. Must be Atoms or Vasprun.")

def phonoatoms2aseatoms(phonoatoms):
    atoms = Atoms(
        phonoatoms.symbols,
        cell=phonoatoms.cell,
        positions=phonoatoms.positions,
        pbc=True
    )
    return atoms

def aseatoms2phonoatoms(atoms):
    phonoatoms = PhonopyAtoms(
        atoms.symbols,
        cell=atoms.cell,
        positions=atoms.positions,
    )
    return phonoatoms

def get_primitive_matrix(config):
    primitive = config['unitcell'].get('primitive_matrix', None)
    atoms = ase_IO.read(config['data']['input'], **config['data']['load_args'])
    if isinstance(primitive, str):
        if primitive.lower() == 'auto':
            bravais = get_spg(atoms)[0]
            return PRIMITIVE_MAP[bravais.lower()]

        else:
            assert primitive.lower() in  PRIMITIVE_MAP.keys()
            return PRIMITIVE_MAP[primitive.lower()]

    elif isinstance(primitive, list):
        assert np.array(primitive).shape == (3, 3), "Primitive matrix must be a 3x3 matrix."
        return primitive.tolist()

    else:
        return PRIMITIVE_MAP['p']  


def check_imaginary_freqs(frequencies: np.ndarray) -> bool:
    try:
        if np.all(np.isnan(frequencies)):
            return True

        if np.any(frequencies[0, 3:] < 0):
            return True

        if np.any(frequencies[0, :3] < -1e-2):
            return True

        if np.any(frequencies[1:] < 0):
            return True
    except Exception as e:
        warnings.warn(f"Failed to check imaginary frequencies: {e}")

    return False

def get_spgnum(atoms, symprec=1e-5):
    cell = (atoms.get_cell(), atoms.get_scaled_positions(), atoms.get_atomic_numbers())
    spgdat = spglib.get_symmetry_dataset(cell, symprec=symprec)
    return spgdat.number

def get_spg(atoms, symprec=1e-5):
    cell = (atoms.get_cell(), atoms.get_scaled_positions(), atoms.get_atomic_numbers())
    spg = spglib.get_spacegroup(cell, symprec=symprec)
    return spg





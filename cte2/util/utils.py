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
    primitive = config['phonon'].get('primitive', None)
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

def get_supercell_matrix(approx_length, cell):
    a, b, c = cell.lengths()

    if not isinstance(approx_length, list):
        approx_length = [approx_length] * 3
    mula = math.ceil(approx_length[0]/a)
    mulb = math.ceil(approx_length[1]/b)
    mulc = math.ceil(approx_length[2]/c)
    return np.diag([mula, mulb, mulc])

def mesh_by_density(density, cell):
    rec_cell = cell.reciprocal()
    a, b, c = rec_cell.lengths()*2*np.pi

    if not isinstance(density, list):
        density = [density] * 3
    mesha = math.ceil(a*density[0])
    meshb = math.ceil(b*density[1])
    meshc = math.ceil(c*density[2])
    return [mesha, meshb, meshc]

def get_band_paths(cell):
    """
    Get band path from ASE.Cell object.
    """
    band = cell.bandpath()
    path = band.path
    if ',' in path:
        path = path.split(',')[0]
    band_path_dict= band.special_points
    band_path = [list(band_path_dict[branch] for branch in path)]
    return band_path

def seek_band_paths(atoms):
    cell = atoms.get_cell()
    scaled_positions = atoms.get_scaled_positions()
    atomic_numbers = atoms.get_atomic_numbers()
    structure = (cell, scaled_positions, atomic_numbers)
    path_data = seekpath.get_path(structure)
    return path_data

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


def _get_strain_list(e_min, e_max, delta=None, Nsteps=None):
    if delta is None and Nsteps is None:
        strain_delta = _get_strain_list(e_min, e_max, delta=0.01)
        strain_steps = _get_strain_list(e_min, e_max, Nsteps=11)
        if len(strain_delta) > len(strain_steps):
            return strain_steps
        else:
            return strain_delta

    if delta is None and Nsteps is not None:
        Nsteps = Nsteps

    else:
        Nsteps = int(round((e_max - e_min) / delta)) + 1

    strain_list = np.linspace(e_min, e_max, Nsteps)
    return strain_list

def _get_suffix_list(e_min, e_max, delta=None, Nsteps=None):
    strain_list = _get_strain_list(e_min, e_max, delta=delta, Nsteps=Nsteps)
    suffix_list = [int(round(e*100)) for e in strain_list]
    return suffix_list

def _get_ratio_list(e_min, e_max, Nsteps=None, delta=None):
    strain_list = _get_strain_list(e_min, e_max, delta=delta, Nsteps=Nsteps)
    ratio_list = [1+strain for strain in strain_list]
    return ratio_list




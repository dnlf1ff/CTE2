import numpy as np
import math
import warnings
import seekpath
from ase.io import write

from ase import Atoms
from ase.cell import Cell
from pymatgen.io.vasp import Vasprun
from pymatgen.core import Structure, Lattice

import spglib
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
from phonopy.interface.vasp import write_supercells_with_displacements

def write_csv(file, atoms, idx='pre', dlm=','):
    if isinstance(atoms, Atoms):
        dct = atoms.info.copy()
        volume=atoms.get_volume()
        a,b,c = atoms.cell().copy().lengths()
        alpha, beta, gamma = atoms.cell().copy().angles()
        try:
            conv = dct['conv']
        except:
            conv = '-'
        file.write(f"{dlm}".join[idx,dct['e_fr_energy'],volume,len(atoms),a,b,c,alpha,beta,gamma,conv] + '\n')

    elif isinstance(atoms, Vasprun):
        if 'pre' in idx:
            dct = atoms.ionic_steps[0].copy()
            conv = '-'
            natoms = len(dct['structure'].sites)
            volume = dct.lattice.volume
            a,b,c = dct.lattice.lengths()
            alpha, beta, gamma = dct.lattice.angles()
        else:
            dct = atoms.ionic_steps[-1].copy()
            conv = atoms.converged
            natoms = len(dct['structure'].sites)
            volume = dct.lattice.volume
            a,b,c = dct.lattice.lengths()
            alpha, beta, gamma = dct.lattice.angles()

        file.write(f"{dlm}".join[idx,dct['e_fr_energy'],volume,natoms,a,b,c,alpha,beta,gamma,conv] + '\n')



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

def get_mesh_numbers(supercell_matrix):
    supercell_matrix = np.array(supercell_matrix)
    if len(supercell_matrix.shape) > 1:
        diag_comp = np.diag(supercell_matrix)
    else:
        diag_comp = supercell_matrix
    normalized = list(diag_comp/diag_comp.max())
    mesh_numbers = []
    for ratio in normalized:
        if ratio < 1:
            mesh_numbers.append(17)
        else:
            mesh_numbers.append(21)
    return [48, 48, 48]

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
        warnings.warn(f"Failed to check imaginary frequencies: {e!r}")

    return False

def get_spgnum(atoms, symprec=1e-5):
    cell = (atoms.get_cell(), atoms.get_scaled_positions(), atoms.get_atomic_numbers())
    spgdat = spglib.get_symmetry_dataset(cell, symprec=symprec)
    return spgdat.number


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



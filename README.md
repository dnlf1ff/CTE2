!! Description

python module for benchmarking the coefficient of thermal expansion (CTE) of mateirals calculated by MLIP(machine learning interatomic potential).

Calculation settings follows phonopy and phono3py's setting (https://github.com/atztogo/phonondb) from the phonondb.

!! Installation

```
micromamba create -n CTENV python==3.10 # (or 3.11 both works)
micromamba activate CTENV
pip install pytorch (check the official git repository of mdil-sevennet for pytorch dependencies)
pip install sevenn
pip install git clone .
```

!! workflow 

<img width="1140" height="661" alt="Screenshot 2025-08-28 at 07 05 47" src="https://github.com/user-attachments/assets/238e1219-7cc1-4c84-b14d-6b814d19e2f6" />

!! Usage

There are two modules
cte2-mlip and cte2-vasp, each coded to automize the same procedure for MLIP as an ASE calculator and VASP.

The following proceudres (calc. FC2, harmonic properties, thermodynamic properties and qha) follow a series of common CLIs: cte2-fc2, cte2-harmonic, and cte2-qha



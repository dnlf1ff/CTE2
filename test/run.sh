#!/bin/bash

# module=$HOME/CTE2
CWD=$(pwd)

# pyright --outputjson > $CWD/debug/pyright.json

cte2-vasp --calc_type vasp --config ./test-input/vasp_config.yaml --prefix Al-VASP --potential_dirname ./test-input --functional pbe54 --task unitcell


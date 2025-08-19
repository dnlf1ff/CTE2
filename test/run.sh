#!/bin/bash

# module=$HOME/CTE2
CWD=$(pwd)

# pyright --outputjson > $CWD/debug/pyright.json

cte2-qha --calc_type sevenn --config ./test-input/vasp_config.yaml --prefix Al-zero --potential_dirname /Users/dnjf/__archive__/MLIP --functional pbe52 --task all --model 7net-0.pth --modal mpa


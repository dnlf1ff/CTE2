#!/bin/bash

module=$HOME/CTE2
CWD=$(pwd)
cd $module/cte2
for d in *; do
    if [ -d "$d" ]; then
        echo "Checking $d"
        cd $d
        pyright --outputjson > $CWD/debug/pyright-$d-.json
        if [ $? -ne 0 ]; then
            echo "Pyright failed for $d"
        else
            echo "Pyright succeeded for $d"
        fi
        cd ..
    fi
done


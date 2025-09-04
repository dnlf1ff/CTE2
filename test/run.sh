#!/bin/bash
#SBATCH --job-name=pyright
#SBATCH --output=pyright.x
#SBATCH --error=pyright.x
#SBATCH --nodes=1   
#SBATCH --ntasks=1
#SBATCH --time=1:00:00 
#SBATCH --partition=gpu

echo "SLURM_NTASKS: $SLURM_NTASKS"

source ~/.bash_profile

if [ -z "$SLURM_NTASKS" ] || [ "$SLURM_NTASKS" -le 0 ]; then
	echo "Error: SLURM_NTASKS is not set or is less than or equal to 0"
	exit 1
fi

source ~/.bashrc
source $CTE_VENV/bin/activate

cd ..
pyright --outputjson > pyright.json



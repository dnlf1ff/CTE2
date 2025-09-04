## Installation & Environmental settings

```
# bash

python -m venv ctenv # python3.11
source ./ctenv/bin/activate
pip install torch==2.5.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install torch-scatter -f https://data.pyg.org/whl/torch-2.5.1+cu121.html
pip install sevenn

git clone git@github.com:dnlf1ff/CTE2.git --branch cte
cd ./cte2
pip install .
```

## Usage

```
# bash
cte2-run ./config.yaml
```

### workflow 

<img width="1140" height="661" alt="Screenshot 2025-08-28 at 07 05 47" src="https://github.com/user-attachments/assets/238e1219-7cc1-4c84-b14d-6b814d19e2f6" />



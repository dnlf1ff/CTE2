## Description

<br>
This is a python package for calculating the coefficient of thermal expansion (CTE) with SevenNet-Omni.
<br>
<img width="856" height="868" alt="workflow" src="https://github.com/user-attachments/assets/e8e018f3-8393-458c-895b-857c2c38f7b0" />  
<br>
You can check out our paper for [SevenNet-Omni](https://github.com/MDIL-SNU/SevenNet/tree/main), used in this work at this [arXiv link](https://arxiv.org/abs/2510.17356).  <br>
<br>
The checkpoint of the model is available at [SevenNet-Omni checkpoint](https://figshare.com/articles/software/SevenNet-Omni_checkpoint/30399814?file=58886557)  <br>
<br>
Don't forget to use the [FlashTP](https://github.com/SNU-ARC/flashTP) kernel for faster, better and stronger calculation. (Cause your time is important)
Tutorials for installing FlashTP package & enabling FlashTP option at our SevenNet calculator are availaable at;  <br>
<br>
[FlashTP installation] (https://github.com/SNU-ARC/flashTP)  <br>
[SevenNet with flash] (https://github.com/MDIL-SNU/SevenNet/tree/flash) (Don't forget to add --branch flash when you clone the repo !)  <br>
<br><br>
The overall workflow of the qhasiharmonic approximation was employed via phonopy.
<br>
## Installation

```
# bash

python -m venv ctenv # python3.11
source ./ctenv/bin/activate
git clone git@github.com:bffntocffn/CTE2.git --branch flash
cd ./cte2
pip install .
```

## Usage

```
# bash
cte2-run --calc seven --model omni --modal mp_r2scan
```





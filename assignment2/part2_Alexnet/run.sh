#!/bin/bash


bash stopservers.sh
bash startservers.sh

python -m AlexNet.scripts.train --mode cluster --dataset flowers --batch_num 2000 --batch_size 32



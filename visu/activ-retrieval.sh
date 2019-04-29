# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
#!/bin/bash

MODEL='../facadevgg/checkpoint.pth.tar'
EXP='./ascent/facadevgg2'
CONV=13
DATA="/home/parawr/Projects/clusterFacadeData/superFacade"

python activ-retrieval.py --model ${MODEL} --exp ${EXP} --conv ${CONV} --data ${DATA}

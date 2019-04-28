# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
#!/bin/bash

DIR="/home/parawr/Projects/clusterFacadeData/superFacade"
ARCH="vgg16"
LR=0.01
WD=-5
K=200
WORKERS=12
EXP="/home/parawr/Projects/deepCluster/facadevgg"
PYTHON="python"
BS=32

mkdir -p ${EXP}

yes | cp -f main.sh ${EXP}
yes | cp -f *.py ${EXP}

CUDA_VISIBLE_DEVICES=1 ${PYTHON} main.py ${DIR} --exp ${EXP} --arch ${ARCH} \
  --lr ${LR} --wd ${WD} --k ${K} --sobel --verbose --workers ${WORKERS} --batch ${BS}

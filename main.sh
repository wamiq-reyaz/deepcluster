# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
#!/bin/bash
NAME=$(hostname)
if [[ $NAME == *"PC"* ]]; then
  DIR="/scratch/dragon/intel/parawr/superFacade/"
else
  DIR="/home/parawr/Projects/clusterFacadeData/superFacade"
fi

ARCH="vgg16"
LR=0.01
WD=-5
K=200
WORKERS=12
EXP="./exp_"${ARCH}/"LR_"${LR}"_WD_"${WD}"_BS_"${BS}"_K_"${K}
PYTHON="python"
BS=32

mkdir -p ${EXP}

yes | cp -f main.sh ${EXP}
yes | cp -f *.py ${EXP}

CUDA_VISIBLE_DEVICES=0 ${PYTHON} main.py ${DIR} --exp ${EXP} --arch ${ARCH} \
  --lr ${LR} --wd ${WD} --k ${K} --sobel --verbose --workers ${WORKERS} --batch ${BS}

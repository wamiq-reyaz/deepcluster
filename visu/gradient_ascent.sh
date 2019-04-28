# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
#!/bin/bash

MODEL='../facadevgg/checkpoint.pth.tar'
ARCH='vgg16'
EXP='./facadevgg2'
CONV=13
LR=9
NITER=10000

CUDA_VISIBLE_DEVICES=0 python gradient_ascent.py --model ${MODEL} --exp ${EXP} --conv ${CONV} --arch ${ARCH} --lr ${LR} --niter ${NITER}

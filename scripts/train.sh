#!/bin/bash
#SBATCH -N 1
#SBATCH --partition=batch
#SBATCH -J cluster
#SBATCH --cores-per-socket=12
#SBATCH -o ../slurm/%J.out
#SBATCH -e ../slurm/%J.out
#SBATCH --mail-user=wamiq.para@kaust.edu.sa
#SBATCH --mail-type=ALL
#SBATCH --time=24:00:00
#SBATCH --mem=36000
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --gres=gpu:v100:1

module add anaconda3
source activate deepcluster

NAME=$(hostname)
if [[ $NAME == *"PC"* ]]; then
  DIR="/home/parawr/Projects/clusterFacadeData/superFacade"
else
  DIR="/scratch/dragon/intel/parawr/fac100k/"
fi

ARCH="vgg16"
LR=0.01
WD=-5
K=200
WORKERS=12
WD_PRINT=${WD//-/m}
WD_PRINT=${WD_PRINT//+/p}
PYTHON="python"
BS=32

EXP="./exp"/${ARCH}/"LR_"${LR}"_WD_"${WD_PRINT}"_BS_"${BS}"_K_"${K}
mkdir -p ${EXP}

yes | cp -f main.sh ${EXP}
yes | cp -f *.py ${EXP}

CUDA_VISIBLE_DEVICES=0 ${PYTHON} ../main.py ${DIR} --exp ${EXP} --arch ${ARCH} \
 --lr ${LR} --wd ${WD} --k ${K} --sobel --verbose --workers ${WORKERS} --batch ${BS}
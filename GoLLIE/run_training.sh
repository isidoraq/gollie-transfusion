#!/bin/bash
#SBATCH --job-name=tf
#SBATCH --output=tf_%a_%j.out
#SBATCH --error=tf_%a_%j.err
#SBATCH --partition="nlprx-lab"
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --gpus-per-node="a10:1"
#SBATCH --qos="short"
#SBATCH --exclude="heistotron,puma,omgwth,cheetah"
#SBATCH -a 1-100
#SBATCH --requeue

# Training
python3 -m src.run configs/model_configs/gollie-tf.yaml
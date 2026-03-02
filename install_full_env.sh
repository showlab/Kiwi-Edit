#!/bin/bash

# Create conda environment
conda create -n diffsynth python=3.10 -y
conda activate diffsynth
# Install PyTorch 2.7 with CUDA
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu128
pip install -e .
conda install mpi4py -y
pip install deepspeed
pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/flash_attn-2.8.3+cu12torch2.7cxx11abiFALSE-cp310-cp310-linux_x86_64.whl
pip install transformers==4.57.0 huggingface-hub==0.34 wandb
mkdir -p models/Wan-AI/
hf download Wan-AI/Wan2.2-TI2V-5B --local-dir ./models/Wan-AI/Wan2.2-TI2V-5B
hf download Wan-AI/Wan2.1-T2V-14B --local-dir ./models/Wan-AI/Wan2.1-T2V-14B
#!/bin/bash

# Create conda environment
conda create -n diffusers python=3.10 -y
conda activate diffusers
# Install PyTorch 2.7 with CUDA
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu128
pip install diffusers einops accelerate transformers==4.57.0 opencv-python av
#!/bin/bash
# SAM3D setup script - run inside the GPU pod
# Requires sam-3d-objects already cloned (via setup.sh in setup-pod)

set -e

WORKSPACE="/workspace"
# inference.py expects CONDA_PREFIX; use CUDA location when not using conda
export CONDA_PREFIX="${CUDA_HOME:-/usr/local/cuda}"

echo "=== SAM3D setup (GPU pod) ==="
echo "CONDA_PREFIX=$CONDA_PREFIX"

echo "=== Installing Python (nvidia/cuda image has none) ==="
apt-get update
apt-get install -y python3 python3-pip

cd "$WORKSPACE/third_party/sam-3d-objects"

echo "=== Installing PyTorch (CUDA 12.1) ==="
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo "=== Installing SAM3D requirements ==="
pip install -r requirements.txt
pip install -r requirements.inference.txt
pip install huggingface_hub

echo "=== Installing SAM3D package ==="
pip install -e .

cd "$WORKSPACE"

echo "=== Verifying SAM3D import ==="
python3 -c "
import sys
sys.path.append('third_party/sam-3d-objects/notebook')
from inference import Inference
print('✓ SAM3D import successful')
"

echo "=== SAM3D setup complete ==="

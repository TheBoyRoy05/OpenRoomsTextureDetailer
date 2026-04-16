#!/bin/bash
# Setup script - run inside the GPU pod (first time only)
# Uses Miniconda on PVC so env persists across pod restarts.
# ORPP-style: flat requirements, manual flash-attn wheel, direct pytorch3d install

set -e

WORKSPACE="/workspace"
CONDA_DIR="$WORKSPACE/miniconda"
CONDA_ENV="sam3d"

echo "=== OpenRoomsTextureDetailer setup (conda on PVC, first run) ==="

cd $WORKSPACE

echo "=== Installing system deps (git, wget, build tools, libGL for Open3D) ==="
apt-get update
apt-get install -y git wget curl build-essential tree unzip libgl1-mesa-glx libglib2.0-0

echo "=== Installing Miniconda to $CONDA_DIR (persists on PVC) ==="
if [ ! -f "$CONDA_DIR/bin/conda" ]; then
    wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
    bash /tmp/miniconda.sh -b -p "$CONDA_DIR"
    rm /tmp/miniconda.sh
    echo "✓ Miniconda installed"
else
    echo "✓ Miniconda already exists"
fi

source "$CONDA_DIR/etc/profile.d/conda.sh"

echo "=== Accepting conda Terms of Service ==="
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 2>/dev/null || true
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r 2>/dev/null || true

echo "=== Creating conda env '$CONDA_ENV' (Python 3.11) ==="
if ! conda env list | grep -q "^${CONDA_ENV} "; then
    conda create -n $CONDA_ENV python=3.11 -y
    echo "✓ Conda env created"
else
    echo "✓ Conda env already exists"
fi

conda activate $CONDA_ENV
export CONDA_PREFIX="$CONDA_DIR/envs/$CONDA_ENV"

PYTHON=python
PIP=pip

echo "=== Cloning SAM3D Objects repository ==="
if [ ! -d "third_party/sam-3d-objects" ]; then
    mkdir -p third_party
    cd third_party
    git clone https://github.com/facebookresearch/sam-3d-objects.git
    cd ..
    echo "✓ SAM3D Objects cloned successfully"
else
    echo "✓ SAM3D Objects already exists"
fi

echo "=== Cloning Trellis2 repository ==="
if [ ! -d "third_party/Trellis2" ]; then
    cd third_party
    git clone https://github.com/your-trellis2-repo.git Trellis2
    cd ..
    echo "✓ Trellis2 cloned successfully"
else
    echo "✓ Trellis2 already exists"
fi

echo "=== PyTorch (pinned 2.5.1 like ORPP) ==="
$PIP install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121

echo "=== Kaolin, hydra, appdirs, nvidia-pyindex ==="
$PIP install kaolin -f https://nvidia-kaolin.s3.us-east-2.amazonaws.com/torch-2.5.1_cu121.html
$PIP install hydra-core appdirs
$PIP install nvidia-pyindex --no-build-isolation

echo "=== SAM3D base requirements (flat, no flash/p3d) ==="
export PIP_EXTRA_INDEX_URL="https://pypi.ngc.nvidia.com https://download.pytorch.org/whl/cu121"
$PIP install -r "$WORKSPACE/scripts/requirements-sam3d.txt"

echo "=== flash-attn prebuilt wheel (ORPP style) ==="
cd /tmp
wget -q "https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.3.11/flash_attn-2.8.0%2Bcu121torch2.5-cp311-cp311-linux_x86_64.whl"
$PIP install flash_attn-2.8.0+cu121torch2.5-cp311-cp311-linux_x86_64.whl
rm -f flash_attn-2.8.0+cu121torch2.5-cp311-cp311-linux_x86_64.whl

echo "=== CUDA env for pytorch3d build ==="
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda}"
export CUDACXX="$CUDA_HOME/bin/nvcc"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib:$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
export NVCC_PREPEND_FLAGS="--allow-unsupported-compiler"
export TORCH_NVCC_FLAGS="--allow-unsupported-compiler"

echo "=== pytorch3d (direct install, --no-build-isolation like ORPP) ==="
$PIP install "git+https://github.com/facebookresearch/pytorch3d.git@75ebeeaea0908c5527e7b1e305fbc7681382db47" --no-build-isolation

echo "=== gsplat (needs torch at build time; install with --no-build-isolation) ==="
$PIP install "git+https://github.com/nerfstudio-project/gsplat.git@2323de5905d5e90e035f792fe65bad0fedd413e7" --no-build-isolation

echo "=== SAM3D inference deps (kaolin, seaborn, gradio) ==="
cd "$WORKSPACE/third_party/sam-3d-objects"
$PIP install -r requirements.inference.txt

echo "=== SAM3D editable install (--no-deps, we have everything) ==="
$PIP install -e . --no-deps

echo "=== Hydra patch ==="
[ -f ./patching/hydra ] && chmod +x ./patching/hydra && ./patching/hydra || echo "hydra patch not found, skipping"

$PIP install huggingface_hub

cd "$WORKSPACE"

echo "=== Verifying SAM3D import ==="
$PYTHON -c "
import sys
sys.path.append('third_party/sam-3d-objects/notebook')
from inference import Inference
print('✓ SAM3D import successful')
"

echo "=== Setup complete ==="
echo ""
echo "Env persists on PVC. On new pods, only run:"
echo "  source /workspace/scripts/activate.sh"
echo ""
ls -la $WORKSPACE

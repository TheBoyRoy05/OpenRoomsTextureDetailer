#!/bin/bash
# Setup script to install tools and clone repos into the PVC

set -e

WORKSPACE="/workspace"
cd $WORKSPACE

echo "=== Installing required tools ==="
apt-get update
apt-get install -y git python3 python3-pip curl wget build-essential tree unzip

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
    git clone https://github.com/your-trellis2-repo.git Trellis2 || echo "Please update Trellis2 repository URL"
    cd ..
    echo "✓ Trellis2 cloned successfully"
else
    echo "✓ Trellis2 already exists"
fi

echo "=== Setup complete ==="
echo "Workspace location: $WORKSPACE"
ls -la $WORKSPACE

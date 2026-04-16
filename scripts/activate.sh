#!/bin/bash
# Activate SAM3D conda env - run on each new pod (after first-time setup)
# Usage: source /workspace/scripts/activate.sh

if [ -f /workspace/miniconda/etc/profile.d/conda.sh ]; then
    source /workspace/miniconda/etc/profile.d/conda.sh
    conda activate sam3d
    echo "✓ sam3d env activated"
else
    echo "Miniconda not found. Run ./scripts/setup.sh first."
fi

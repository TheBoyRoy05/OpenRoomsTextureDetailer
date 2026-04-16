# OpenRoomsTextureDetailer

## Overview
This project is a pipeline for generating texture details for open rooms. It uses SAM3D to generate 3D meshes and Trellis2 to texture them. It is designed to run on the Nautilus cluster. Every path will be relative to the `/workspace` directory.

## Prerequisites
- Access to `undergrad-ms` namespace
- PVC `open-rooms-texture-detailer-vol` (see Volumes below)

## Volumes
- `volumes/main-pvc.yaml`
  - open-rooms-texture-detailer-vol
  - rook-ceph-block
  - 256Gi

## Pods
- `pods/explore-pod.yaml`
  - Lightweight pod for exploring storage (no GPU)
  - name: explore-storage
  - image: ubuntu:22.04
  - resource limits: 100m CPU, 256Mi RAM
- `pods/gpu-pod.yaml`
  - GPU pod for SAM3D and computational tasks
  - name: gpu-pod
  - image: nvidia/cuda:12.1.0-devel-ubuntu22.04
  - resource limits: 1 GPU, 4 CPU, 16Gi RAM
  - **Requires 32GB+ VRAM** (SAM3D). Node selector requests A100-80GB. If the pod stays Pending, try `Tesla-V100-SXM2-32GB` or `NVIDIA-L40S` in the nodeSelector.

**Note:** The volume uses ReadWriteOnce. Only one pod can use it at a time. Delete the GPU pod before starting the explore pod, and vice versa.

## Setup

### Quick reference

| Situation | What to do |
|-----------|------------|
| **First time** (fresh PVC or new project) | Run setup (Step 3). Takes 20–40 min. |
| **New pod** (after setup is done) | Just activate (Step 4). Takes ~1 sec. |

### Step 1: Deploy volume (if not already created)

```bash
kubectl apply -f volumes/main-pvc.yaml
```

### Step 2: Deploy GPU pod

```bash
kubectl apply -f pods/gpu-pod.yaml
kubectl get pods -w   # wait for Running
```

### Step 3: First-time setup (run once)

Copy scripts and exec into the pod:

```bash
POD=gpu-pod
kubectl cp scripts $POD:/workspace/scripts
kubectl exec -it $POD -- bash
```

Inside the pod:

```bash
cd /workspace
sed -i 's/\r$//' scripts/*.sh   # required if copied from Windows
chmod +x scripts/setup.sh scripts/activate.sh
./scripts/setup.sh
```

### Step 4: New pod (after first setup)

The conda env persists on the PVC. Activate it:

```bash
sed -i 's/\r$//' /workspace/scripts/activate.sh  # if copied from Windows
source /workspace/scripts/activate.sh
```

### Step 5: Verify setup (~2 minutes)

```bash
cd /workspace
source /workspace/scripts/activate.sh
python -c "import sys; sys.path.append('third_party/sam-3d-objects/notebook'); from inference import Inference; print('SAM3D import successful')"
```

### Step 6: Run SAM3D test (optional)

Place an image and mask at `/workspace/input/image.png` and `/workspace/input/mask.png`, then:

```bash
source /workspace/scripts/activate.sh
python scripts/SAM3D-test.py
```

## Using Pods

Set namespace:

```bash
kubectl config set-context --current --namespace=undergrad-ms
```

Get pod name:

```bash
POD=$(kubectl get pods -l app=gpu-pod -o jsonpath='{.items[0].metadata.name}')
```

Copy files to pod:

```bash
kubectl cp <local-path> $POD:<remote-path>
```

Shell into pod:

```bash
kubectl exec -it $POD -- bash
cd /workspace
source /workspace/scripts/activate.sh   # activate SAM3D env
```

### View images via HTTP server

In the pod (with conda activated):

```bash
python -m http.server 8000
```

On your machine:

```bash
kubectl port-forward $POD 8080:8000
```

Then open http://localhost:8080

## Scripts
- `scripts/setup.sh`
  - Run in gpu-pod **first time only**. Installs Miniconda to PVC, clones SAM3D Objects and Trellis2, installs PyTorch 2.5.1, SAM3D (ORPP-style). Takes 20–40 min.
- `scripts/activate.sh`
  - Run on **each new pod** (after first setup). Activates the conda env. Usage: `source /workspace/scripts/activate.sh`
- `scripts/requirements-sam3d.txt`
  - SAM3D base deps (excludes torch, flash_attn, pytorch3d; those are installed separately)
- `scripts/download_images.py`
  - Downloads HyperSim scene to `/workspace/downloads` and `/workspace/images`
- `scripts/list_images.py`
  - Generates an HTML image viewer of downloaded images
- `scripts/view_images.sh`
  - Starts an HTTP server to view images

### TRELLIS.2 (separate setup)

TRELLIS.2 uses its own conda env and PyTorch/CUDA versions. To set it up, clone and run its official setup:

```bash
cd /workspace/third_party
git clone -b main https://github.com/microsoft/TRELLIS.2.git --recursive
cd TRELLIS.2
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm
```

Use `conda activate trellis2` when running TRELLIS.2.

## Data Persistence

All data in `/workspace` is persisted in the PVC:
- Miniconda and conda env (`miniconda/`, `sam3d` env with all packages)
- Cloned repositories (`third_party/sam-3d-objects`, `third_party/Trellis2`)
- Downloaded images
- Generated 3D meshes and textures

On a new pod, run `source /workspace/scripts/activate.sh`—no need to rerun setup.

## References

- [Nautilus Storage Documentation](https://nrp.ai/documentation/userdocs/storage/ceph/)
- [Nautilus GPU Pods](https://nrp.ai/documentation/userdocs/running/)
- [Moving Data](https://nrp.ai/documentation/userdocs/storage/move-data/)

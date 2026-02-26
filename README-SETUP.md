# Nautilus Cluster Setup for SAM3D and Trellis2 Pipeline

## Overview
This setup configures a persistent volume on the Nautilus cluster for running SAM3D (3D mesh generation) and Trellis2 (texturing) pipelines.

## Prerequisites
- Access to `undergrad-ms` namespace
- PVC `test-vol` already created (256Gi, rook-ceph-block)

## Step 1: Deploy Setup Pod

Deploy a pod to clone repositories into your PVC:

```bash
kubectl apply -f setup-pod.yaml
```

Wait for the pod to be ready:
```bash
kubectl get pods -n undergrad-ms -w
```

## Step 2: Clone Repositories

Execute into the pod:
```bash
kubectl exec -it -n undergrad-ms deployment/setup-pod -- bash
```

Inside the pod, run the setup script:
```bash
cd /workspace
apt-get update
apt-get install -y git python3 python3-pip curl wget build-essential

# Clone SAM3D Objects
mkdir -p third_party
cd third_party
git clone https://github.com/facebookresearch/sam-3d-objects.git
cd ..

# Clone Trellis2 (update URL as needed)
cd third_party
git clone <TRELLIS2_REPO_URL> Trellis2
cd ..
```

Or copy the setup script and run it:
```bash
kubectl cp setup-script.sh undergrad-ms/setup-pod-<pod-id>:/tmp/setup.sh
kubectl exec -it -n undergrad-ms deployment/setup-pod -- bash -c "chmod +x /tmp/setup.sh && /tmp/setup.sh"
```

## Step 3: Deploy GPU Pod for SAM3D

For running SAM3D (requires GPU):
```bash
kubectl apply -f gpu-pod.yaml
```

Wait for GPU pod to be ready:
```bash
kubectl get pods -n undergrad-ms -w
```

Execute into GPU pod:
```bash
kubectl exec -it -n undergrad-ms sam3d-gpu-pod -- bash
```

## Step 4: Install Dependencies

Inside the GPU pod, install SAM3D dependencies:

```bash
cd /workspace/third_party/sam-3d-objects

# Install Python dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
pip install -r requirements.inference.txt
pip install huggingface_hub

# Install SAM3D package
pip install -e .
```

## Step 5: Verify Setup

Check that everything is accessible:
```bash
cd /workspace
ls -la third_party/
python3 -c "import sys; sys.path.append('third_party/sam-3d-objects/notebook'); from inference import Inference; print('SAM3D import successful')"
```

## Managing Pods

### Stop a pod (without deleting):
```bash
kubectl scale deployment setup-pod --replicas=0 -n undergrad-ms
```

### Start a pod:
```bash
kubectl scale deployment setup-pod --replicas=1 -n undergrad-ms
```

### Delete GPU pod when done:
```bash
kubectl delete pod sam3d-gpu-pod -n undergrad-ms
```

## Data Persistence

All data in `/workspace` is persisted in the PVC `test-vol`. This includes:
- Cloned repositories (`third_party/sam-3d-objects`, `third_party/Trellis2`)
- Installed packages and dependencies
- Generated 3D meshes and textures
- Your pipeline code

## Next Steps

1. Update `SAM3D-test.py` to use the correct paths
2. Set up Trellis2 dependencies
3. Develop your pipeline script
4. Create batch jobs for processing multiple images

## References

- [Nautilus Storage Documentation](https://nrp.ai/documentation/userdocs/storage/ceph/)
- [Nautilus GPU Pods](https://nrp.ai/documentation/userdocs/running/)
- [Moving Data](https://nrp.ai/documentation/userdocs/storage/move-data/)

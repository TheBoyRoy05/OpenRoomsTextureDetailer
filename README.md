# OpenRoomsTextureDetailer

## Overview
This project is a pipeline for generating texture details for open rooms. It uses SAM3D to generate 3D meshes and Trellis2 to texture them. It is designed to run on the Nautilus cluster. Every path will be relative to the `/workspace` directory.

**Note:** The volume persists data (repos, images) but not installed tools. Run `setup.sh` (setup-pod) and `setup_sam3d.sh` (gpu-pod) each time you start a fresh pod.

## Volumes
- `main-pvc.yaml`
  - open-rooms-texture-detailer-vol 
  - rook-ceph-block
  - 256Gi

## Pods
- `explore-pod.yaml`
  - Lightweight pod for exploring storage
  - name: explore-storage
  - image: ubuntu:22.04
  - resource limits: 100m CPU, 256Mi RAM
- `setup-pod.yaml`
  - Pod for cloning repos and setup
  - name: setup-pod
  - image: ubuntu:22.04
  - resource limits: 2 CPU, 8Gi RAM
- `gpu-pod.yaml`
  - GPU pod for computational tasks
  - name: sam3d-gpu-pod
  - image: nvidia/cuda:12.1.0-devel-ubuntu22.04
  - resource limits: 1 GPU, 4 CPU, 16Gi RAM

### Using Pods
Get and set namespace using 
```bash
kubectl config get-contexts
kubectl config set-context --current --namespace=undergrad-ms
```

Deploy a pod
```bash
kubectl apply -f <pod>.yaml
```

Wait until it’s running
```bash
kubectl get pods -w
```

Set pod name
```bash
POD=<pod-name>
```

Copying files to pod
```bash
kubectl cp <local-path> $POD:<remote-path>
```

Shell into the pod
```bash
kubectl exec -it $POD -- bash
cd workspace
```

Exit and remove pod when done
```bash
exit
kubectl delete pod $POD
```

### Using HTTP server to view images
From the running pod
```bash
cd images
python3 -m http.server <pod-port>
```

On your machine
```bash
kubectl port-forward $POD <local-port>:<pod-port>
```

## Scripts
- `setup.sh`
  - Run in setup-pod. Installs git, Python, etc.
  - Clones SAM3D Objects and Trellis2 into `/workspace/third_party`
- `setup_sam3d.sh`
  - Run in gpu-pod. Installs PyTorch, SAM3D deps, and verifies import.
- `download_images.py`
  - Downloads HyperSim scene to `/downloads` and `/images`
- `list_images.py`
  - Generates an HTML image viewer of downloaded images
- `view_images.sh`
  - Starts an HTTP server to view images
  - Has port forwarding instructions

#!/usr/bin/env python3
"""
SAM3D test script for Nautilus cluster
Assumes repos are cloned in /workspace/third_party/
Run with: source /workspace/scripts/activate.sh && python scripts/SAM3D-test.py
"""
import sys
import os

# Add the notebook directory to the path for inference imports
WORKSPACE = "/workspace"
SAM3D_PATH = os.path.join(WORKSPACE, "third_party", "sam-3d-objects", "notebook")
sys.path.append(SAM3D_PATH)

from inference import Inference, load_image, load_mask

def main():
    print("=== SAM3D Test Script ===")
    
    # Download checkpoints from HuggingFace (per sam-3d-objects doc/setup.md)
    # Requires: request access at https://huggingface.co/facebook/sam-3d-objects, then huggingface-cli login
    checkpoint_dir = os.path.join(WORKSPACE, "third_party", "sam-3d-objects", "checkpoints", "hf")
    config_path = os.path.join(checkpoint_dir, "pipeline.yaml")
    
    if not os.path.exists(config_path):
        print("Downloading SAM3D checkpoints from HuggingFace...")
        from huggingface_hub import snapshot_download
        download_dir = os.path.join(WORKSPACE, "third_party", "sam-3d-objects", "checkpoints", "hf-download")
        snapshot_download(
            repo_id="facebook/sam-3d-objects",
            repo_type="model",
            local_dir=download_dir,
        )
        # Reorganize: move checkpoints/hf-download/checkpoints -> checkpoints/hf
        import shutil
        inner = os.path.join(download_dir, "checkpoints")
        if os.path.exists(inner):
            os.makedirs(os.path.dirname(checkpoint_dir), exist_ok=True)
            if os.path.exists(checkpoint_dir):
                shutil.rmtree(checkpoint_dir)
            shutil.move(inner, checkpoint_dir)
        shutil.rmtree(download_dir, ignore_errors=True)
        print(f"Checkpoints saved to {checkpoint_dir}")
    else:
        print(f"Using checkpoints at {checkpoint_dir}")
    
    # Initialize inference
    print("Initializing inference pipeline...")
    inference = Inference(config_path, compile=False)
    print("✓ Inference pipeline ready")
    
    # Load image and mask
    image_path = os.path.join(WORKSPACE, "input", "image.png")
    mask_path = os.path.join(WORKSPACE, "input", "mask.png")
    if not os.path.exists(image_path):
        image_path = os.path.join(WORKSPACE, "input", "test_image.jpg")
    if not os.path.exists(mask_path):
        mask_path = os.path.join(WORKSPACE, "input", "0.png")  # fallback: load_single_mask uses 0.png
    
    if not os.path.exists(image_path):
        print(f"Warning: Image not found. Place image at /workspace/input/image.png or test_image.jpg")
        return
    
    if not os.path.exists(mask_path):
        print(f"Warning: Mask not found. Place mask at /workspace/input/mask.png or 0.png")
        return
    
    print(f"Loading image from {image_path}")
    image = load_image(image_path)
    
    print(f"Loading mask from {mask_path}")
    mask = load_mask(mask_path)
    
    # Run inference
    print("Running inference...")
    output = inference(image, mask, seed=42)
    
    # Save output
    output_dir = os.path.join(WORKSPACE, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save Gaussian splat
    if "gs" in output:
        output_path = os.path.join(output_dir, "splat.ply")
        output["gs"].save_ply(output_path)
        print(f"✓ Saved Gaussian splat to {output_path}")
    
    print("=== Inference complete ===")

if __name__ == "__main__":
    main()

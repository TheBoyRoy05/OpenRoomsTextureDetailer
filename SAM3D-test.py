#!/usr/bin/env python3
"""
SAM3D test script for Nautilus cluster
Assumes repos are cloned in /workspace/third_party/
"""
import sys
import os

# Add the notebook directory to the path for inference imports
WORKSPACE = "/workspace"
SAM3D_PATH = os.path.join(WORKSPACE, "third_party", "sam-3d-objects", "notebook")
sys.path.append(SAM3D_PATH)

from inference import Inference, load_image, load_single_mask
from huggingface_hub import hf_hub_download

def main():
    print("=== SAM3D Test Script ===")
    
    # Download pipeline config from HuggingFace
    print("Downloading pipeline config...")
    path = hf_hub_download("facebook/sam-3d-objects", "pipeline.yaml")
    print(f"Config downloaded to: {path}")
    
    # Initialize inference
    print("Initializing inference pipeline...")
    inference = Inference(path, compile=False)
    print("✓ Inference pipeline ready")
    
    # Load image and mask (update paths as needed)
    image_path = os.path.join(WORKSPACE, "input", "image.png")
    mask_path = os.path.join(WORKSPACE, "input", "mask.png")
    
    if not os.path.exists(image_path):
        print(f"Warning: Image not found at {image_path}")
        print("Please place your image at /workspace/input/image.png")
        return
    
    if not os.path.exists(mask_path):
        print(f"Warning: Mask not found at {mask_path}")
        print("Please place your mask at /workspace/input/mask.png")
        return
    
    print(f"Loading image from {image_path}")
    image = load_image(image_path)
    
    print(f"Loading mask from {mask_path}")
    mask = load_single_mask(os.path.dirname(mask_path), index=0)
    
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

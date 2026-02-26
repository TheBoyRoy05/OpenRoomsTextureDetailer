#!/usr/bin/env python3
"""
Download images script optimized for Nautilus workspace
Downloads to /workspace by default
"""
import argparse
import os

# Default to workspace directory
WORKSPACE = "/workspace"

# 1. Setup Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--downloads_dir", default=os.path.join(WORKSPACE, "downloads"), 
                    help=f"Directory to download archives (default: {WORKSPACE}/downloads)")
parser.add_argument("--decompress_dir", default=os.path.join(WORKSPACE, "images"),
                    help=f"Directory to decompress images (default: {WORKSPACE}/images)")
parser.add_argument("--delete_archive_after_decompress", action="store_true",
                    help="Delete zip files after decompression")
args = parser.parse_args()

print(f"[DOWNLOAD_IMAGES] Downloads dir: {args.downloads_dir}")
print(f"[DOWNLOAD_IMAGES] Decompress dir: {args.decompress_dir}")
print("[DOWNLOAD_IMAGES] Begin...")

if not os.path.exists(args.downloads_dir):
    os.makedirs(args.downloads_dir)
    print(f"Created directory: {args.downloads_dir}")

if args.decompress_dir is not None:
    if not os.path.exists(args.decompress_dir):
        os.makedirs(args.decompress_dir)
        print(f"Created directory: {args.decompress_dir}")
        
def download(url):
    download_name = os.path.basename(url)
    download_file = os.path.join(args.downloads_dir, download_name)
    cmd = f"curl -L {url} --output {download_file}"
    print(f"\nDownloading: {url}")
    print(f"Command: {cmd}\n")
    if os.system(cmd) != 0:
        raise RuntimeError("Download failed.")
    
    if args.decompress_dir is not None:
        cmd = f"unzip -o {download_file} -d {args.decompress_dir}"
        print(f"\nDecompressing to: {args.decompress_dir}")
        print(f"Command: {cmd}\n")
        if os.system(cmd) != 0:
             raise RuntimeError("Unzip failed.")
        if args.delete_archive_after_decompress:
            cmd = f"rm {download_file}"
            print(f"\nDeleting archive: {download_file}\n")
            os.system(cmd)

# Add your URLs here
urls_to_download = [
    "https://docs-assets.developer.apple.com/ml-research/datasets/hypersim/v1/scenes/ai_001_001.zip"
]

for url in urls_to_download:
    download(url)

print("\n✓ Finished downloading images.")
print(f"Images available at: {args.decompress_dir if args.decompress_dir else args.downloads_dir}")

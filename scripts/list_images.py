#!/usr/bin/env python3
"""
List and display information about images in the workspace
"""
import os
import sys
from pathlib import Path

WORKSPACE = "/workspace"
IMAGE_DIRS = [
    os.path.join(WORKSPACE, "images"),
    os.path.join(WORKSPACE, "downloads"),
]

def get_image_files(directory):
    """Get all image files from a directory recursively"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    image_files = []
    
    if not os.path.exists(directory):
        return image_files
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, directory)
                size = os.path.getsize(full_path)
                image_files.append({
                    'path': full_path,
                    'relative': f"images/{rel_path}",
                    'size': size,
                    'size_mb': size / (1024 * 1024)
                })
    
    return image_files

def main():
    print("=" * 60)
    print("Image Viewer - Listing images in workspace")
    print("=" * 60)
    
    all_images = []
    for img_dir in IMAGE_DIRS:
        print(f"\nScanning: {img_dir}")
        images = get_image_files(img_dir)
        all_images.extend(images)
        print(f"Found {len(images)} images")
    
    if not all_images:
        print("\nNo images found in workspace directories.")
        print(f"Searched in: {', '.join(IMAGE_DIRS)}")
        return
    
    print(f"\n{'=' * 60}")
    print(f"Total images found: {len(all_images)}")
    print(f"{'=' * 60}\n")
    
    # Group by directory
    by_dir = {}
    for img in all_images:
        dir_path = os.path.dirname(img['relative'])
        if dir_path not in by_dir:
            by_dir[dir_path] = []
        by_dir[dir_path].append(img)
    
    # Display summary
    for dir_path, images in sorted(by_dir.items()):
        print(f"\nDirectory: {dir_path if dir_path else '(root)'}")
        print(f"  Images: {len(images)}")
        total_size = sum(img['size_mb'] for img in images)
        print(f"  Total size: {total_size:.2f} MB")
        print(f"  Files:")
        for img in sorted(images, key=lambda x: x['relative'])[:10]:  # Show first 10
            print(f"    - {img['relative']} ({img['size_mb']:.2f} MB)")
        if len(images) > 10:
            print(f"    ... and {len(images) - 10} more")
    
    # Generate HTML viewer
    html_content = generate_html_viewer(all_images)
    html_path = os.path.join(WORKSPACE, "image_viewer.html")
    with open(html_path, 'w') as f:
        f.write(html_content)
    print(f"\n{'=' * 60}")
    print(f"HTML viewer generated: {html_path}")
    print(f"To view: Start HTTP server and open image_viewer.html")
    print(f"{'=' * 60}")

def generate_html_viewer(images):
    """Generate a simple HTML page to view images"""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Workspace Image Viewer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; }
        .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .image-card { background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .image-card img { width: 100%; height: auto; border-radius: 4px; }
        .image-info { margin-top: 10px; font-size: 12px; color: #666; }
        .image-path { word-break: break-all; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Workspace Images (""" + str(len(images)) + """)</h1>
        <div class="image-grid">
"""
    
    for img in images:
        # Use relative path for images
        img_path = img['relative'].replace('\\', '/')
        html += f"""
            <div class="image-card">
                <img src="{img_path}" alt="{img['relative']}" onerror="this.style.display='none'">
                <div class="image-info">
                    <div class="image-path">{img['relative']}</div>
                    <div>Size: {img['size_mb']:.2f} MB</div>
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    main()

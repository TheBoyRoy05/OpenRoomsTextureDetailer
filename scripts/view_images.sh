#!/bin/bash
# Simple HTTP server to view images in workspace
# Run this inside your pod

PORT=${1:-8080}
IMAGE_DIR=${2:-/workspace/images}

echo "Starting image viewer server..."
echo "Image directory: $IMAGE_DIR"
echo "Port: $PORT"
echo ""
echo "To access from your local machine, run:"
echo "  kubectl port-forward -n undergrad-ms <pod-name> $PORT:$PORT"
echo ""
echo "Then open: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$IMAGE_DIR"
python3 -m http.server "$PORT"

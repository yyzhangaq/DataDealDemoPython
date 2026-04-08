#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="csv-cleaner-task:latest"

echo "Building Docker image..."
docker build -t "$IMAGE_NAME" -f "$PROJECT_DIR/environment/Dockerfile" "$PROJECT_DIR"

echo "Running cleaner.py inside container..."
docker run --rm -v "$PROJECT_DIR:/workspace" -w /data "$IMAGE_NAME" python3 cleaner.py dirty_data.csv /workspace/cleaned_data.csv

exit 0
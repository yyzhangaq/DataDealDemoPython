#!/bin/bash
# Run the CSV cleaner reference solution inside Docker
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="csv-cleaner-cli"

echo "Building Docker image..."
docker build -t "$IMAGE_NAME" -f "$PROJECT_DIR/environment/Dockerfile" "$PROJECT_DIR"

echo "Running cleaner.py inside container..."
docker run --rm "$IMAGE_NAME" python3 /app/cleaner.py

exit 0

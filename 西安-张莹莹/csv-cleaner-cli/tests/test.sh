#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "[TEST] ======================================="
echo "[TEST] CSV Cleaner CLI Test Suite"
echo "[TEST] ======================================="

echo "[TEST] Step 1: Building Docker image..."
docker build -f environment/Dockerfile -t csv-cleaner-task:latest .
echo "[TEST] Docker image built successfully"

echo "[TEST] Step 2: Running cleaner to process dirty data..."
docker run --rm csv-cleaner-task:latest python3 /data/cleaner.py /data/dirty_data.csv /data/cleaned_data.csv

echo "[TEST] Step 3: Running validation to verify cleaned data..."
docker run --rm csv-cleaner-task:latest python3 /data/test_logic.py

echo "[TEST] ======================================="
echo "[TEST] All tests passed successfully!"
echo "[TEST] ========================================"
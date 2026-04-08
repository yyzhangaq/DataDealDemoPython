#!/bin/bash

# ============================================================
# CSV Cleaner CLI - Debug Test Script
# ============================================================

set -x  # 开启调试模式

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "DEBUG: SCRIPT_DIR=$SCRIPT_DIR"
echo "DEBUG: PROJECT_ROOT=$PROJECT_ROOT"

cd "$PROJECT_ROOT" || { echo "ERROR: Cannot cd to $PROJECT_ROOT"; exit 1; }

echo "DEBUG: Current directory after cd: $(pwd)"

# 检查文件
echo "DEBUG: Checking required files..."
ls -la environment/Dockerfile
ls -la environment/dirty_data.csv
ls -la solution/cleaner.py
ls -la tests/test_logic.py

# 构建 Docker 镜像
echo "DEBUG: Building Docker image..."
docker build -f environment/Dockerfile -t csv-cleaner-task:latest . || { echo "ERROR: Docker build failed"; exit 1; }

# 运行 cleaner.py
echo "DEBUG: Running cleaner.py..."
docker run --rm \
    -v "$PROJECT_ROOT:/workspace" \
    -w /workspace \
    csv-cleaner-task:latest \
    python3 solution/cleaner.py environment/dirty_data.csv cleaned_data.csv

echo "DEBUG: cleaner.py exit code: $?"

# 检查输出文件
echo "DEBUG: Checking for cleaned_data.csv..."
ls -la cleaned_data.csv

# 运行验证
echo "DEBUG: Running test_logic.py..."
docker run --rm \
    -v "$PROJECT_ROOT:/workspace" \
    -w /workspace \
    csv-cleaner-task:latest \
    python3 tests/test_logic.py cleaned_data.csv

echo "DEBUG: test_logic.py exit code: $?"

set +x  # 关闭调试模式
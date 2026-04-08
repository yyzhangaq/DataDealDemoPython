#!/bin/bash

# ============================================================
# CSV Cleaner CLI - Test Entry Script
# 必须返回 exit code 0（成功）或 1（失败）
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT" || { echo "ERROR: Cannot cd to $PROJECT_ROOT"; exit 1; }

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 错误处理函数
handle_error() {
    local msg="$1"
    log_error "$msg"
    log_error "Test suite FAILED"
    exit 1
}

# ============================================================
# 开始测试
# ============================================================
log_info "=========================================="
log_info "CSV Cleaner CLI Test Suite"
log_info "Start time: $(date '+%Y-%m-%d %H:%M:%S')"
log_info "=========================================="

# ============================================================
# Step 1: 检查必要文件
# ============================================================
log_step "Step 1/5: Checking required files..."

required_files=(
    "environment/Dockerfile"
    "environment/dirty_data.csv"
    "solution/cleaner.py"
    "tests/test_logic.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        handle_error "Required file not found: $file"
    fi
done

log_info "All required files exist"

# ============================================================
# Step 2: 构建 Docker 镜像
# ============================================================
log_step "Step 2/5: Building Docker image..."

build_output=$(docker build -f environment/Dockerfile -t csv-cleaner-task:latest . 2>&1)
build_exit=$?

if [ $build_exit -ne 0 ]; then
    log_error "Docker build failed with exit code: $build_exit"
    echo "$build_output" | tail -20
    handle_error "Docker build failed"
fi

log_info "Docker image built successfully"

# ============================================================
# Step 3: 运行 cleaner.py
# ============================================================
log_step "Step 3/5: Running cleaner.py to process dirty data..."

if [ -f "cleaned_data.csv" ]; then
    rm -f "cleaned_data.csv"
    log_info "Removed existing cleaned_data.csv"
fi

run_output=$(docker run --rm \
    -v "$PROJECT_ROOT:/workspace" \
    -w /data \
    csv-cleaner-task:latest \
    python3 cleaner.py dirty_data.csv /workspace/cleaned_data.csv 2>&1)

run_exit=$?

if [ $run_exit -ne 0 ]; then
    log_error "cleaner.py execution failed with exit code: $run_exit"
    echo "$run_output" | tail -30
    handle_error "cleaner.py execution failed"
fi

log_info "cleaner.py executed successfully"

# ============================================================
# Step 4: 验证输出文件
# ============================================================
log_step "Step 4/5: Verifying output file..."

if [ ! -f "cleaned_data.csv" ]; then
    handle_error "cleaned_data.csv was not created by cleaner.py"
fi

if [ ! -s "cleaned_data.csv" ]; then
    handle_error "cleaned_data.csv is empty"
fi

file_size=$(wc -c < "cleaned_data.csv")
log_info "cleaned_data.csv created (size: $file_size bytes)"

# ============================================================
# Step 5: 运行测试验证
# ============================================================
log_step "Step 5/5: Running validation tests..."

test_output=$(docker run --rm \
    -v "$PROJECT_ROOT:/workspace" \
    -w /workspace \
    csv-cleaner-task:latest \
    python3 tests/test_logic.py cleaned_data.csv 2>&1)

test_exit=$?

if [ $test_exit -ne 0 ]; then
    log_error "Validation tests failed with exit code: $test_exit"
    echo "$test_output" | tail -30
    handle_error "Validation tests failed"
fi

log_info "All validation tests passed"

# ============================================================
# 全部通过
# ============================================================
log_info "=========================================="
log_info "✅ All tests passed successfully!"
log_info "End time: $(date '+%Y-%m-%d %H:%M:%S')"
log_info "=========================================="

exit 0
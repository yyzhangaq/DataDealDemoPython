#!/bin/bash
# Test entry script for CSV Cleaner CLI
# Runs in CLEAN Linux environment — only bash + docker available on host
# All Python logic executes INSIDE Docker container
# Returns exit code 0 if all tests pass, 1 if any test fails

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="csv-cleaner-cli"
CONTAINER_NAME="csv-cleaner-test-$$"

echo "============================================================"
echo "CSV Cleaner CLI — Docker Test Runner"
echo "============================================================"
echo ""

echo "[Step 1/3] Building Docker image..."
echo "------------------------------------------------------------"

if [ ! -f "$PROJECT_DIR/environment/Dockerfile" ]; then
    echo "Error: Dockerfile not found at $PROJECT_DIR/environment/Dockerfile"
    exit 1
fi

docker build -t "$IMAGE_NAME" -f "$PROJECT_DIR/environment/Dockerfile" "$PROJECT_DIR"

BUILD_EXIT=$?
if [ $BUILD_EXIT -ne 0 ]; then
    echo "Error: docker build failed with exit code $BUILD_EXIT"
    exit 1
fi

echo ""
echo "✓ Docker image built successfully"
echo ""

echo "[Step 2/3] Running cleaner.py inside container..."
echo "[Step 3/3] Running validation tests inside container..."
echo "------------------------------------------------------------"
echo "(Both steps run in the same container so cleaned_data.csv persists)"
echo ""

docker run --rm \
    --name "$CONTAINER_NAME" \
    "$IMAGE_NAME" \
    bash -c "
        echo '--- Running cleaner.py ---'
        python3 /app/cleaner.py
        CLEANER_EXIT=\$?
        if [ \$CLEANER_EXIT -ne 0 ]; then
            echo 'Error: cleaner.py exited with code '\$CLEANER_EXIT
            exit 1
        fi
        echo ''
        echo '--- Running test_logic.py ---'
        python3 /app/test_logic.py
    "

TEST_EXIT=$?

echo ""
if [ $TEST_EXIT -eq 0 ]; then
    echo "============================================================"
    echo "RESULT: ALL TESTS PASSED ✅"
    echo "============================================================"
else
    echo "============================================================"
    echo "RESULT: SOME TESTS FAILED ❌"
    echo "============================================================"
fi

exit $TEST_EXIT

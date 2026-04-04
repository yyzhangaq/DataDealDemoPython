#!/bin/bash
# Test entry script for CSV Cleaner CLI
# Returns exit code 0 if all tests pass, 1 if any test fails

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "============================================================"
echo "Setting up test environment..."
echo "============================================================"

# Copy dirty data to working directory if not present
if [ ! -f "dirty_data.csv" ]; then
    if [ -f "environment/dirty_data.csv" ]; then
        cp environment/dirty_data.csv ./dirty_data.csv
        echo "Copied dirty_data.csv from environment/"
    else
        echo "Error: dirty_data.csv not found in environment/"
        exit 1
    fi
fi

# Check if cleaner.py exists (AI should have created it)
if [ ! -f "cleaner.py" ]; then
    echo "Error: cleaner.py not found in project root"
    echo "The AI should create cleaner.py that reads dirty_data.csv and outputs cleaned_data.csv"
    exit 1
fi

echo "Running cleaner.py..."
echo ""

# Run the cleaner — capture exit code without set -e
python3 cleaner.py
CLEANER_EXIT=$?

if [ $CLEANER_EXIT -ne 0 ]; then
    echo ""
    echo "Error: cleaner.py exited with code $CLEANER_EXIT"
    exit 1
fi

# Check if output was created
if [ ! -f "cleaned_data.csv" ]; then
    echo ""
    echo "Error: cleaned_data.csv was not created by cleaner.py"
    exit 1
fi

echo ""
echo "Running validation tests..."
echo ""

# Run the test logic
python3 tests/test_logic.py
TEST_EXIT=$?

exit $TEST_EXIT

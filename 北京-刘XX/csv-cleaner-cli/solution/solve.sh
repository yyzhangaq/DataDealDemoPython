#!/bin/bash
# Run the CSV cleaner reference solution
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Copy dirty data if not already present
if [ ! -f "dirty_data.csv" ]; then
    cp environment/dirty_data.csv ./dirty_data.csv
fi

python3 solution/cleaner.py

exit 0

#!/bin/bash
set -e
cp environment/dirty_data.csv dirty_data.csv
python solution/cleaner.py

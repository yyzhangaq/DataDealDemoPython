#!/usr/bin/env python3
import csv
import sys


def load_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.reader(f))


def main():
    actual = load_csv('cleaned_data.csv')
    expected = load_csv('solution/expected_output.csv')

    if len(actual) != len(expected):
        print(fFAIL": Row count mismatch: got {len(actual)}, expected {len(expected)}")
        sys.exit(1)

    for i, (a_row, e_row) in enumerate(zip(actual, expected)):
        if a_row != e_row:
            print(f"FAIL: Row {i} mismatch")
            print(f"  Actual:   {a_row}")
            print(f"  Expected: {e_row}")
            sys.exit(1)

    print("PASS: All rows match expected output")
    print(f"Total rows verified: {len(actual)}")


if __name__ == '__main__':
    main()

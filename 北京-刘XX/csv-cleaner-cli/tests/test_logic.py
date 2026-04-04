#!/usr/bin/env python3
"""
Test logic for CSV Cleaner CLI
Validates that the cleaning operations are correctly implemented.
Includes both positive checks and negative (anti-cheat) checks.
"""

import csv
import os
import sys
import re
from pathlib import Path


def load_csv(filepath: str) -> list:
    """Load CSV file and return list of rows."""
    with open(filepath, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        return [row for row in reader]


def load_raw_bytes(filepath: str) -> bytes:
    """Load file as raw bytes for encoding checks."""
    with open(filepath, 'rb') as f:
        return f.read()


class TestResult:
    """Accumulates test results with pass/fail/warn."""
    def __init__(self):
        self.results = []
        self.failed = False

    def fail(self, msg):
        self.results.append(f"  FAIL: {msg}")
        self.failed = True

    def pass_(self, msg):
        self.results.append(f"  PASS: {msg}")

    def warn(self, msg):
        self.results.append(f"  WARN: {msg}")

    def section(self, title):
        self.results.append(f"\n[{title}]")


def run_tests(cleaned_file: str, dirty_file: str, expected_file: str) -> tuple:
    """Run all validation tests. Returns (passed: bool, messages: list)."""
    t = TestResult()

    # ========================================================
    # Section 1: Basic file checks
    # ========================================================
    t.section("Basic File Checks")

    if not os.path.exists(cleaned_file):
        t.fail("Output file 'cleaned_data.csv' not found")
        return not t.failed, t.results

    raw_bytes = load_raw_bytes(cleaned_file)

    if len(raw_bytes) == 0:
        t.fail("Output file is empty (0 bytes)")
        return not t.failed, t.results

    t.pass_("Output file exists and is non-empty")

    try:
        cleaned_rows = load_csv(cleaned_file)
    except Exception as e:
        t.fail(f"Cannot parse output as CSV: {e}")
        return not t.failed, t.results

    try:
        dirty_rows = load_csv(dirty_file)
    except Exception:
        dirty_rows = None

    t.pass_("Output file is valid CSV")

    # ========================================================
    # Section 2: Anti-cheat — output must differ from input
    # ========================================================
    t.section("Anti-Cheat Checks")

    if dirty_rows and cleaned_rows == dirty_rows:
        t.fail("Output is identical to input — no cleaning was performed (copy detected)")
    else:
        t.pass_("Output differs from input")

    if dirty_rows:
        dirty_data_count = len(dirty_rows) - 1
        cleaned_data_count = len(cleaned_rows) - 1 if cleaned_rows else 0
        if cleaned_data_count >= dirty_data_count:
            t.fail(f"Row count not reduced (dirty={dirty_data_count}, cleaned={cleaned_data_count}): cleaning may not have occurred")
        else:
            t.pass_(f"Row count reduced: {dirty_data_count} -> {cleaned_data_count}")

    # ========================================================
    # Section 3: Header validation
    # ========================================================
    t.section("Header Validation")

    expected_header = ['id', 'name', 'email', 'age', 'city', 'signup_date', 'score']

    if not cleaned_rows:
        t.fail("Output has no rows at all")
        return not t.failed, t.results

    header = cleaned_rows[0]
    header_trimmed = [h.strip() for h in header]

    if header_trimmed != expected_header:
        t.fail(f"Header mismatch. Expected {expected_header}, got {header_trimmed}")
    else:
        t.pass_("Header is correct")

    # Check header has no whitespace
    if header != header_trimmed:
        t.fail("Header fields contain untrimmed whitespace")
    else:
        t.pass_("Header fields are trimmed")

    # ========================================================
    # Section 4: Empty row removal
    # ========================================================
    t.section("Empty Row Removal")

    empty_row_count = 0
    for i, row in enumerate(cleaned_rows[1:], start=2):
        if all(cell.strip() == '' for cell in row):
            empty_row_count += 1
            t.fail(f"Row {i} is an empty/whitespace-only row that should have been removed")

    if empty_row_count == 0:
        t.pass_("No empty rows remain")

    # ========================================================
    # Section 5: Whitespace trimming
    # ========================================================
    t.section("Whitespace Trimming")

    untrimmed_cells = []
    for i, row in enumerate(cleaned_rows):
        for j, cell in enumerate(row):
            if cell != cell.strip():
                untrimmed_cells.append((i + 1, j + 1, repr(cell)))

    if untrimmed_cells:
        for row_num, col_num, val in untrimmed_cells[:5]:
            t.fail(f"Untrimmed whitespace at row {row_num}, col {col_num}: {val}")
        if len(untrimmed_cells) > 5:
            t.fail(f"... and {len(untrimmed_cells) - 5} more untrimmed cells")
    else:
        t.pass_("All cells are properly trimmed")

    # ========================================================
    # Section 6: Duplicate removal
    # ========================================================
    t.section("Duplicate Removal")

    seen = set()
    dup_count = 0
    for i, row in enumerate(cleaned_rows[1:], start=2):
        row_tuple = tuple(row)
        if row_tuple in seen:
            dup_count += 1
            t.fail(f"Duplicate row at line {i}: {row[:3]}...")
        seen.add(row_tuple)

    if dup_count == 0:
        t.pass_("No duplicate rows")

    # ========================================================
    # Section 7: Encoding checks
    # ========================================================
    t.section("Encoding Checks")

    # No BOM in output
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        t.fail("Output file contains BOM — should have been removed")
    else:
        t.pass_("No BOM in output")

    # No non-printable characters
    non_printable_pattern = re.compile(rb'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')
    np_matches = non_printable_pattern.findall(raw_bytes)
    if np_matches:
        t.fail(f"Output contains {len(np_matches)} non-printable character(s)")
    else:
        t.pass_("No non-printable characters in output")

    # No \r\n in output
    if b'\r\n' in raw_bytes or b'\r' in raw_bytes:
        t.fail("Output contains \\r (carriage return) — line endings not normalized to \\n")
    else:
        t.pass_("Line endings are normalized to LF")

    # ========================================================
    # Section 8: Column alignment
    # ========================================================
    t.section("Column Alignment")

    expected_col_count = len(expected_header)
    misaligned = []
    for i, row in enumerate(cleaned_rows):
        if len(row) != expected_col_count:
            misaligned.append((i + 1, len(row)))

    if misaligned:
        for row_num, col_count in misaligned[:5]:
            t.fail(f"Row {row_num} has {col_count} columns, expected {expected_col_count}")
    else:
        t.pass_(f"All rows have {expected_col_count} columns")

    # ========================================================
    # Section 9: Date normalization
    # ========================================================
    t.section("Date Normalization")

    date_col_idx = None
    if expected_header and 'signup_date' in expected_header:
        date_col_idx = expected_header.index('signup_date')

    if date_col_idx is not None:
        iso_date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        bad_dates = []
        for i, row in enumerate(cleaned_rows[1:], start=2):
            if date_col_idx < len(row):
                val = row[date_col_idx].strip()
                if val and not iso_date_pattern.match(val):
                    bad_dates.append((i, val))

        if bad_dates:
            for row_num, val in bad_dates[:5]:
                t.fail(f"Row {row_num}: date '{val}' is not in ISO 8601 format (YYYY-MM-DD)")
        else:
            t.pass_("All dates are in ISO 8601 format")
    else:
        t.warn("signup_date column not found — skipping date checks")

    # ========================================================
    # Section 10: Expected row count
    # ========================================================
    t.section("Row Count Validation")

    expected_unique_records = 15
    actual_data_rows = len(cleaned_rows) - 1

    if actual_data_rows != expected_unique_records:
        t.fail(f"Expected {expected_unique_records} unique data rows, got {actual_data_rows}")
    else:
        t.pass_(f"Correct number of unique data rows: {expected_unique_records}")

    # ========================================================
    # Section 11: Golden file comparison (exact match)
    # ========================================================
    t.section("Golden File Comparison")

    if os.path.exists(expected_file):
        try:
            expected_rows = load_csv(expected_file)
            if cleaned_rows == expected_rows:
                t.pass_("Output exactly matches expected golden file")
            else:
                # Find first difference
                max_rows = max(len(cleaned_rows), len(expected_rows))
                diff_count = 0
                for i in range(max_rows):
                    if i >= len(cleaned_rows):
                        t.fail(f"Missing row {i + 1} in output (expected: {expected_rows[i][:3]}...)")
                        diff_count += 1
                    elif i >= len(expected_rows):
                        t.fail(f"Extra row {i + 1} in output: {cleaned_rows[i][:3]}...")
                        diff_count += 1
                    elif cleaned_rows[i] != expected_rows[i]:
                        t.fail(f"Row {i + 1} mismatch:")
                        t.fail(f"  Expected: {expected_rows[i]}")
                        t.fail(f"  Got:      {cleaned_rows[i]}")
                        diff_count += 1

                    if diff_count >= 5:
                        t.fail(f"... (showing first 5 differences only)")
                        break
        except Exception as e:
            t.warn(f"Could not load golden file for comparison: {e}")
    else:
        t.warn("Golden file (expected_output.csv) not found — skipping exact comparison")

    return not t.failed, t.results


def main():
    """Main test entry point."""
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent

    cleaned_file = project_dir / "cleaned_data.csv"
    dirty_file = project_dir / "dirty_data.csv"
    expected_file = project_dir / "solution" / "expected_output.csv"

    # Fallback to environment directory for dirty data
    if not dirty_file.exists():
        dirty_file = project_dir / "environment" / "dirty_data.csv"

    print("=" * 60)
    print("CSV Cleaner CLI — Test Suite")
    print("=" * 60)

    passed, messages = run_tests(str(cleaned_file), str(dirty_file), str(expected_file))

    for msg in messages:
        print(msg)

    print()
    print("=" * 60)

    if passed:
        print("RESULT: ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("RESULT: SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
CSV Cleaner CLI Tool — Reference Solution
Cleans messy CSV data according to the rules defined in instruction.md.
"""

import csv
import sys
import re
from pathlib import Path
from datetime import datetime


def remove_bom(text: str) -> str:
    """Remove UTF-8 BOM if present."""
    if text.startswith('\ufeff'):
        return text[1:]
    return text


def remove_non_printable(text: str) -> str:
    """Remove non-printable characters (0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F, 0x7F-0x9F)."""
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)


def is_empty_row(row: list) -> bool:
    """Check if a row is empty or contains only whitespace."""
    return all(cell.strip() == '' for cell in row)


def normalize_date(value: str) -> str:
    """Normalize various date formats to ISO 8601 (YYYY-MM-DD)."""
    value = value.strip()
    if not value:
        return value

    # Already ISO format: YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        return value

    # YYYY/MM/DD
    if re.match(r'^\d{4}/\d{2}/\d{2}$', value):
        try:
            dt = datetime.strptime(value, '%Y/%m/%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return value

    # MM/DD/YYYY
    if re.match(r'^\d{2}/\d{2}/\d{4}$', value):
        try:
            dt = datetime.strptime(value, '%m/%d/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return value

    # DD-MM-YYYY
    if re.match(r'^\d{2}-\d{2}-\d{4}$', value):
        try:
            dt = datetime.strptime(value, '%d-%m-%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return value

    # Month DD, YYYY (e.g., "March 15, 2023")
    try:
        dt = datetime.strptime(value, '%B %d, %Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    return value


def pad_or_truncate_row(row: list, expected_cols: int) -> list:
    """Fix column count: pad with empty strings or truncate."""
    if len(row) < expected_cols:
        return row + [''] * (expected_cols - len(row))
    elif len(row) > expected_cols:
        return row[:expected_cols]
    return row


def clean_csv(input_path: str, output_path: str) -> None:
    """
    Clean a CSV file by applying all rules in order:
    1. Fix encoding (BOM, non-printable chars)
    2. Normalize line endings (handled by reading mode)
    3. Fix column alignment
    4. Remove empty rows
    5. Trim whitespace
    6. Normalize dates in signup_date column
    7. Remove duplicate rows
    """
    input_file = Path(input_path)

    if not input_file.exists():
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)

    # Read raw bytes to handle BOM and mixed line endings
    raw = input_file.read_bytes()

    # Rule 1: Remove BOM
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]

    # Rule 2: Normalize line endings to \n
    text = raw.decode('utf-8', errors='replace')
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Rule 1 continued: Remove non-printable characters from entire text
    text = remove_non_printable(text)

    # Parse CSV
    import io
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    if not rows:
        print("Error: Input file is empty.", file=sys.stderr)
        sys.exit(1)

    # Rule 5: Trim whitespace on header first (needed for column name detection)
    header = [cell.strip() for cell in rows[0]]
    expected_cols = len(header)

    # Find the signup_date column index (for Rule 6)
    date_col_idx = None
    for i, col_name in enumerate(header):
        if col_name == 'signup_date':
            date_col_idx = i
            break

    cleaned_rows = [header]
    seen_rows = set()

    for row in rows[1:]:
        # Rule 4: Remove empty rows
        if is_empty_row(row):
            continue

        # Rule 3: Fix column alignment
        row = pad_or_truncate_row(row, expected_cols)

        # Rule 5: Trim whitespace
        row = [cell.strip() for cell in row]

        # Rule 6: Normalize dates
        if date_col_idx is not None and date_col_idx < len(row):
            row[date_col_idx] = normalize_date(row[date_col_idx])

        # Rule 7: Remove duplicates
        row_tuple = tuple(row)
        if row_tuple in seen_rows:
            continue
        seen_rows.add(row_tuple)

        cleaned_rows.append(row)

    # Write output with consistent \n line endings
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(cleaned_rows)

    total = len(cleaned_rows) - 1
    print(f"Successfully cleaned CSV: {total} data rows written to '{output_path}'")


def main():
    clean_csv('dirty_data.csv', 'cleaned_data.csv')


if __name__ == '__main__':
    main()

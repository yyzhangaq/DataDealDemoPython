#!/usr/bin/env python3
import csv
import sys
import re
from pathlib import Path
from datetime import datetime


def remove_bom(text: str) -> str:
    if text.startswith('\ufeff'):
        return text[1:]
    return text


def remove_non_printable(text: str) -> str:
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)


def is_empty_row(row: list) -> bool:
    return all(cell.strip() == '' for cell in row)


def normalize_date(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        return value
    if re.match(r'^\d{4}/\d{2}/\d{2}$', value):
        try:
            dt = datetime.strptime(value, '%Y/%m/%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return value
    if re.match(r'^\d{2}/\d{2}/\d{4}$', value):
        try:
            dt = datetime.strptime(value, '%m/%d/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return value
    if re.match(r'^\d{2}-\d{2}-\d{4}$', value):
        try:
            dt = datetime.strptime(value, '%d-%m-%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return value
    try:
        dt = datetime.strptime(value, '%B %d, %Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    return value


def pad_or_truncate_row(row: list, expected_cols: int) -> list:
    if len(row) < expected_cols:
        return row + [''] * (expected_cols - len(row))
    elif len(row) > expected_cols:
        return row[:expected_cols]
    return row


def clean_csv(input_path: str, output_path: str) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)

    raw = input_file.read_bytes()
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]

    text = raw.decode('utf-8', errors='replace')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = remove_non_printable(text)

    import io
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    if not rows:
        print("Error: Input file is empty.", file=sys.stderr)
        sys.exit(1)

    header = [cell.strip() for cell in rows[0]]
    expected_cols = len(header)

    date_col_idx = None
    for i, col_name in enumerate(header):
        if col_name == 'signup_date':
            date_col_idx = i
            break

    cleaned_rows = [header]
    seen_rows = set()

    for row in rows[1:]:
        if is_empty_row(row):
            continue
        row = pad_or_truncate_row(row, expected_cols)
        row = [cell.strip() for cell in row]
        if date_col_idx is not None and date_col_idx < len(row):
            row[date_col_idx] = normalize_date(row[date_col_idx])
        row_tuple = tuple(row)
        if row_tuple in seen_rows:
            continue
        seen_rows.add(row_tuple)
        cleaned_rows.append(row)

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(cleaned_rows)

    total = len(cleaned_rows) - 1
    print(f"Successfully cleaned CSV: {total} data rows written to '{output_path}'")


def main():
    clean_csv('dirty_data.csv', 'cleaned_data.csv')


if __name__ == '__main__':
    main()

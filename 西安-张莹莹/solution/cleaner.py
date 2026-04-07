#!/usr/bin/env python3
"""
CSV Cleaner CLI Tool
Cleans messy CSV data according to the rules defined in instruction.md.
Uses line-by-line text processing to handle embedded commas in unquoted fields.
"""

import sys
import re
from pathlib import Path
from datetime import datetime


STRIP_NONPRINT = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')
ISO_DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def strip_nonprint(text: str) -> str:
    return STRIP_NONPRINT.sub('', text)


def is_all_blank(fields: list) -> bool:
    return all(f.strip() == '' for f in fields)


def parse_csv_line(line: str) -> list:
    result = []
    field = ''
    in_quote = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            if in_quote:
                if i + 1 < len(line) and line[i + 1] == '"':
                    field += '"'
                    i += 1
                else:
                    in_quote = False
            else:
                in_quote = True
        elif ch == ',' and not in_quote:
            result.append(field)
            field = ''
        else:
            field += ch
        i += 1
    result.append(field)
    return result


def try_parse_date(value: str) -> str:
    v = value.strip()
    if not v:
        return v
    if ISO_DATE.match(v):
        return v

    if re.match(r'^\d{4}/\d{2}/\d{2}$', v):
        try:
            return datetime.strptime(v, '%Y/%m/%d').strftime('%Y-%m-%d')
        except ValueError:
            pass

    if re.match(r'^\d{2}/\d{2}/\d{4}$', v):
        for fmt in ('%m/%d/%Y', '%d/%m/%Y'):
            try:
                return datetime.strptime(v, fmt).strftime('%Y-%m-%d')
            except ValueError:
                pass

    if re.match(r'^\d{2}-\d{2}-\d{4}$', v):
        dd_mm_valid = False
        mm_dd_valid = False
        try:
            datetime.strptime(v, '%d-%m-%Y')
            dd_mm_valid = True
        except ValueError:
            pass
        try:
            datetime.strptime(v, '%m-%d-%Y')
            mm_dd_valid = True
        except ValueError:
            pass
        if dd_mm_valid:
            return datetime.strptime(v, '%d-%m-%Y').strftime('%Y-%m-%d')
        if mm_dd_valid:
            return datetime.strptime(v, '%m-%d-%Y').strftime('%Y-%m-%d')

    for fmt in ('%B %d, %Y', '%B %d %Y', '%b %d, %Y', '%b %d %Y'):
        try:
            return datetime.strptime(v, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass

    return value


def fix_row_embedded_comma(row: list) -> list:
    result = []
    i = 0
    while i < len(row):
        if i + 1 < len(row):
            merged = try_parse_date(row[i] + ', ' + row[i + 1])
            if merged != row[i] + ', ' + row[i + 1]:
                result.append(merged)
                i += 2
                continue
        result.append(row[i])
        i += 1
    return result


def pad_row(row: list, target: int) -> list:
    if len(row) < target:
        return row + [''] * (target - len(row))
    return row[:target]


def clean_csv(input_path: str, output_path: str) -> None:
    inp = Path(input_path)
    if not inp.exists():
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)

    raw = inp.read_bytes()
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]

    text = raw.decode('utf-8', errors='replace')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = strip_nonprint(text)

    lines = text.split('\n')
    while lines and lines[-1].strip() == '':
        lines.pop()

    if not lines:
        print("Error: Input file is empty.", file=sys.stderr)
        sys.exit(1)

    header = parse_csv_line(lines[0].strip())
    header = [h.strip() for h in header]
    num_cols = len(header)

    signup_date_idx = None
    for i, col in enumerate(header):
        if col == 'signup_date':
            signup_date_idx = i
            break

    cleaned_lines_out = [','.join(header)]
    seen = set()

    for line in lines[1:]:
        stripped_line = line.strip()
        if stripped_line == '':
            continue

        fields = parse_csv_line(stripped_line)
        fields = [f.strip() for f in fields]

        if is_all_blank(fields):
            continue

        fields = fix_row_embedded_comma(fields)
        fields = pad_row(fields, num_cols)
        fields = [f.strip() for f in fields]

        if signup_date_idx is not None and signup_date_idx < len(fields):
            fields[signup_date_idx] = try_parse_date(fields[signup_date_idx])

        row_key = tuple(fields)
        if row_key in seen:
            continue
        seen.add(row_key)

        cleaned_lines_out.append(','.join(fields))

    out_text = '\n'.join(cleaned_lines_out) + '\n'
    out_bytes = out_text.encode('utf-8')
    Path(output_path).write_bytes(out_bytes)

    data_rows = len(cleaned_lines_out) - 1
    print(f"Successfully cleaned CSV: {data_rows} data rows written to '{output_path}'")


def main():
    clean_csv('dirty_data.csv', 'cleaned_data.csv')


if __name__ == '__main__':
    main()

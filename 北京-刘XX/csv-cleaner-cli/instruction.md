# CSV Cleaner CLI

## Task Description

Create a Python command-line tool that cleans messy CSV data. The tool should read a dirty CSV file, apply a set of well-defined cleaning operations, and output a cleaned CSV file.

## Input

- A file named `dirty_data.csv` located in the current working directory
- The file may contain various data quality issues including encoding problems, structural errors, and formatting inconsistencies

## Output

- A cleaned CSV file named `cleaned_data.csv` in the current working directory

## Cleaning Rules (must implement ALL)

Your tool must apply the following operations **in the specified order**:

### Rule 1: Fix Encoding Issues
- Remove BOM (Byte Order Mark) if present at the beginning of the file
- Remove non-printable characters (ASCII `0x00`-`0x08`, `0x0B`, `0x0C`, `0x0E`-`0x1F`, `0x7F`-`0x9F`) from all cell values
- Preserve standard printable characters and UTF-8 multibyte characters

### Rule 2: Normalize Line Endings
- Convert all line endings to Unix-style `\n` (LF)
- The output file must use `\n` consistently

### Rule 3: Fix Column Alignment
- The first row is the header; count the number of columns from the header
- Rows with **fewer columns** than the header: pad with empty strings at the end
- Rows with **more columns** than the header: truncate extra columns from the end

### Rule 4: Remove Empty Rows
- Remove any row (after the header) where **all fields** are empty or contain only whitespace
- A row with at least one non-whitespace value must be kept

### Rule 5: Trim Whitespace
- Strip leading and trailing whitespace from **every cell** value (including the header)

### Rule 6: Normalize Date Fields
- The column named `signup_date` contains dates in mixed formats
- Normalize all dates to ISO 8601 format: `YYYY-MM-DD`
- Supported input formats to handle:
  - `MM/DD/YYYY` (e.g., `03/15/2023`)
  - `DD-MM-YYYY` (e.g., `15-03-2023`)
  - `Month DD, YYYY` (e.g., `March 15, 2023`)
  - `YYYY/MM/DD` (e.g., `2023/03/15`)
  - `YYYY-MM-DD` (already correct, keep as-is)
- If a date value cannot be parsed, keep the original value unchanged

### Rule 7: Remove Duplicate Rows
- After all cleaning is applied, remove exact duplicate rows (keep the **first** occurrence)
- Comparison is based on the cleaned values (after trimming, date normalization, etc.)

## Usage

```bash
python cleaner.py
```

The script must:
- Read from `dirty_data.csv` in the current directory
- Write the cleaned output to `cleaned_data.csv` in the current directory
- Exit with code `0` on success
- Exit with a non-zero code on failure (e.g., input file not found)

## Constraints

- Use only Python standard library (no external dependencies like `pandas`)
- Must work with Python 3.11
- Handle files encoded in UTF-8 (with or without BOM)
- Do not reorder rows (preserve the original row order, minus removed rows)
- Do not reorder columns

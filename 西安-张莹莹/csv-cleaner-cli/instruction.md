# CSV Cleaner CLI Task

## Task Description
Write a Python CLI tool that cleans messy CSV data containing user records with name, email, and age fields.

## Requirements

### Input Data Format
The dirty CSV file (`dirty_data.csv`) contains the following columns:
- `name`: User's full name
- `email`: User's email address
- `age`: User's age (numeric)

### Data Cleaning Rules
1. **Name**: Remove leading/trailing whitespace; reject empty names
2. **Email**:
   - Remove leading/trailing whitespace
   - Convert to lowercase
   - Validate format (must contain @ and a valid domain)
   - Reject invalid email formats
3. **Age**:
   - Must be a valid integer between 1 and 149
   - Reject invalid or out-of-range values
4. **Deduplication**: Remove duplicate rows (same name + email + age combination)
5. **Empty rows**: Skip rows where all fields are empty

### Output
- Write cleaned data to `cleaned_data.csv`
- Output format: `name,email,age` (header row followed by data rows)
- All cleaned emails must be lowercase
- No duplicate rows in output

### Running the Solution
```bash
python3 cleaner.py <input_csv> <output_csv>
```

Example:
```bash
python3 cleaner.py /data/dirty_data.csv /data/cleaned_data.csv
```

### Expected Behavior
- The cleaner must process the input CSV and produce a clean output CSV
- Invalid rows should be skipped (not included in output)
- The tool should print the number of cleaned rows to stdout
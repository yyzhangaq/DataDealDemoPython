#!/usr/bin/env python3
import csv
import sys
import os

def test_cleaned_data(cleaned_path):
    """
    验证清洗后的CSV文件
    验证规则：
    1. 文件必须存在
    2. 不能为空
    3. 每行必须有有效的name（非空）
    4. 每行必须有有效的email（含@且全小写）
    5. 每行必须有有效的age（1-149之间的整数）
    6. 不能有重复行
    """
    if not os.path.exists(cleaned_path):
        print(f"[ERROR] cleaned_data.csv not found at {cleaned_path}")
        sys.exit(1)

    with open(cleaned_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if len(rows) == 0:
        print("[ERROR] cleaned_data.csv is empty")
        sys.exit(1)

    for i, row in enumerate(rows):
        name = row.get('name', '').strip()
        email = row.get('email', '').strip()
        age = row.get('age', '').strip()

        if not name:
            print(f"[ERROR] Row {i+1} has empty name")
            sys.exit(1)

        if not email or '@' not in email:
            print(f"[ERROR] Row {i+1} has invalid email: {email}")
            sys.exit(1)

        if not email.islower():
            print(f"[ERROR] Row {i+1} email not lowercase: {email}")
            sys.exit(1)

        try:
            age_int = int(age)
            if age_int <= 0 or age_int >= 150:
                print(f"[ERROR] Row {i+1} has invalid age: {age}")
                sys.exit(1)
        except:
            print(f"[ERROR] Row {i+1} age not valid int: {age}")
            sys.exit(1)

    seen = set()
    for row in rows:
        key = (row['name'], row['email'], row['age'])
        if key in seen:
            print(f"[ERROR] Duplicate row found: {key}")
            sys.exit(1)
        seen.add(key)

    print(f"[PASS] Validation passed: {len(rows)} rows cleaned correctly")

if __name__ == '__main__':
    print("[TEST] Starting validation...")
    cleaned_path = sys.argv[1] if len(sys.argv) > 1 else '/data/cleaned_data.csv'
    test_cleaned_data(cleaned_path)
    print("[TEST] Validation completed successfully")
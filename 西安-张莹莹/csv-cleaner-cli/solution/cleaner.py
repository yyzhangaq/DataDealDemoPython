#!/usr/bin/env python3
import csv
import sys
import re
import os

def clean_email(email):
    """清洗email地址：去空格、转小写、验证格式"""
    email = email.strip().lower()
    return email if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) else None

def clean_age(age):
    """清洗年龄：必须是1-149之间的有效整数"""
    try:
        age = int(age.strip())
        return age if 0 < age < 150 else None
    except:
        return None

def clean_name(name):
    """清洗姓名：去空格，非空"""
    name = name.strip()
    return name if name else None

def clean_csv(input_path, output_path):
    """
    清洗CSV数据
    清洗规则：
    1. name: 去除首尾空格，空值跳过
    2. email: 去除首尾空格，转小写，验证格式，无效跳过
    3. age: 必须是1-149之间的有效整数
    4. 去重：相同(name, email, age)的行只保留一条
    5. 空行跳过
    """
    cleaned_rows = []
    seen = set()

    print(f"[INFO] Reading input file: {input_path}")
    with open(input_path, 'r', encoding='utf-8', newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = [f.strip() for f in reader.fieldnames]
        print(f"[INFO] Input columns: {fieldnames}")

        total_rows = 0
        valid_rows = 0
        skipped_rows = 0
        duplicate_rows = 0

        for row in reader:
            total_rows += 1
            if not any(row.values()):
                print(f"[SKIP] Row {total_rows}: empty row")
                skipped_rows += 1
                continue

            name = clean_name(row.get('name', '').strip())
            email = clean_email(row.get('email', '').strip())
            age = clean_age(row.get('age', '').strip())

            if name is None:
                print(f"[SKIP] Row {total_rows}: invalid name '{row.get('name', '')}'")
                skipped_rows += 1
                continue
            if email is None:
                print(f"[SKIP] Row {total_rows}: invalid email '{row.get('email', '')}'")
                skipped_rows += 1
                continue
            if age is None:
                print(f"[SKIP] Row {total_rows}: invalid age '{row.get('age', '')}'")
                skipped_rows += 1
                continue

            key = (name, email, age)
            if key in seen:
                print(f"[SKIP] Row {total_rows}: duplicate of (name={name}, email={email}, age={age})")
                duplicate_rows += 1
                continue
            seen.add(key)
            valid_rows += 1
            cleaned_rows.append({'name': name, 'email': email, 'age': age})

    print(f"[INFO] Writing output file: {output_path}")
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['name', 'email', 'age'])
        writer.writeheader()
        writer.writerows(cleaned_rows)

    print(f"[SUMMARY] Total: {total_rows}, Valid: {valid_rows}, Skipped: {skipped_rows}, Duplicates: {duplicate_rows}")
    return len(cleaned_rows)

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else '/data/dirty_data.csv'
    output_file = sys.argv[2] if len(sys.argv) > 2 else '/data/cleaned_data.csv'
    count = clean_csv(input_file, output_file)
    print(f"[DONE] Cleaned {count} rows, output written to {output_file}")
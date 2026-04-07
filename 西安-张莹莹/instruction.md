# 任务说明

## 任务描述

构建一个 Python CLI 工具，对脏数据 CSV 文件进行清洗，输出干净的 CSV 文件。

## 输入

- `dirty_data.csv`：位于当前工作目录，包含各种数据质量问题

## 输出

- `cleaned_data.csv`：清洗后的 CSV 文件

## 清洗规则（必须按顺序执行）

### Rule 1: 修复编码问题
- 移除文件开头的 BOM
- 移除所有单元格中的不可打印字符（ASCII `0x00`-`0x08`, `0x0B`, `0x0C`, `0x0E`-`0x1F`, `0x7F`-`0x9F`）

### Rule 2: 规范化换行符
- 统一转换为 Unix 风格 `\n`（LF）

### Rule 3: 修复列对齐
- 以 header 列为基准
- 列数不足 → 末尾填充空字符串
- 列数过多 → 截断多余列

### Rule 4: 移除空行
- 移除所有字段均为空或仅含空格的行

### Rule 5: 去除前后空格
- trim 所有单元格（包括 header）

### Rule 6: 规范化日期字段
- `signup_date` 列中混合格式日期统一为 ISO 8601：`YYYY-MM-DD`
- 支持格式：`MM/DD/YYYY`、`DD-MM-YYYY`、`Month DD, YYYY`、`YYYY/MM/DD`、`YYYY-MM-DD`
- 无法解析的日期保持原值

### Rule 7: 移除重复行
- 清洗完成后移除完全重复的行（保留首条）

## 使用方式

```bash
python cleaner.py
```

- 从当前目录读取 `dirty_data.csv`
- 输出 `cleaned_data.csv` 到当前目录
- 成功 exit 0，失败 exit 非零
- 仅使用 Python 标准库

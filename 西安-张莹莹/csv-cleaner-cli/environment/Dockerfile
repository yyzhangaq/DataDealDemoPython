FROM python:3.11.4-slim

WORKDIR /data

COPY environment/dirty_data.csv /data/dirty_data.csv
COPY solution/cleaner.py /data/cleaner.py
COPY tests/test_logic.py /data/test_logic.py

RUN chmod +x /data/cleaner.py /data/test_logic.py

CMD ["python3", "/data/cleaner.py", "/data/dirty_data.csv", "/data/cleaned_data.csv"]
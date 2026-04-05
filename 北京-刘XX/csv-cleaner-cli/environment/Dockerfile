FROM python:3.11.9-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        bash=5.2.15-2+b7 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY environment/dirty_data.csv /app/dirty_data.csv
COPY solution/cleaner.py /app/cleaner.py
COPY solution/expected_output.csv /app/expected_output.csv
COPY tests/test_logic.py /app/test_logic.py

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

CMD ["bash"]

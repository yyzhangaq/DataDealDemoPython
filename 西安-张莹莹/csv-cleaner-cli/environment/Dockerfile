FROM python:3.11.9-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /data

ADD solution/cleaner.py /data/cleaner.py
ADD environment/dirty_data.csv /data/dirty_data.csv

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["bash"]
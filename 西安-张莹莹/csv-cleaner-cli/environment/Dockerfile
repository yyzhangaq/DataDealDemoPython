FROM python:3.11.9-slim-bookworm

# 只安装必要的系统包（不装 pandas/pytest 等，除非必须）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# 不在这里ADD代码，运行时通过 -v 挂载

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["bash"]
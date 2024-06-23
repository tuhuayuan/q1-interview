FROM python:3.11.4-slim-bullseye

RUN apt-get update && apt-get install -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.8.3
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# 安装项目
RUN poetry install --only main

# Removing gcc
RUN apt-get purge -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# 拷贝项目代码设置工作目录
COPY . /app/src/
RUN poetry install --only main

CMD ["uvicorn", "q1_api:app", "--host", "0.0.0.0"]
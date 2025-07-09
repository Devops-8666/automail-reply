# Dockerfile

FROM python:3.10-slim

WORKDIR /app
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    openssl \
    && rm -rf /var/lib/apt/lists/*

RUN update-ca-certificates

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "run.py"]


# Dockerfile

FROM python:3.10-slim

WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/app

CMD ["supervisord", "-c", "/app/supervisord.conf"]	


# Dockerfile

FROM python:3.10-slim

WORKDIR /app
RUN apt-get update && apt-get install -y libssl-dev ca-certificates

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python3", "run.py"]


FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip \
    chromium chromium-driver \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8090

CMD ["python", "app.py"]

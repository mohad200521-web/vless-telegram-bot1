FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip \
    -o /tmp/xray.zip \
    && mkdir -p /usr/local/bin/xray \
    && unzip /tmp/xray.zip -d /usr/local/bin/xray \
    && chmod +x /usr/local/bin/xray/xray \
    && rm /tmp/xray.zip

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .
COPY xray_api.py .
COPY config.json /etc/xray/config.json

EXPOSE 8080

CMD ["/bin/sh", "-c", "/usr/local/bin/xray/xray run -config /etc/xray/config.json & python bot.py"]
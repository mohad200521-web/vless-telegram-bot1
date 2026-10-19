FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends 
curl unzip ca-certificates 
&& rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip 
-o /tmp/xray.zip 
&& unzip -o /tmp/xray.zip xray -d /usr/local/bin/ 
&& chmod +x /usr/local/bin/xray 
&& rm /tmp/xray.zip

WORKDIR /app

COPY config.json /app/config.json

EXPOSE 8080

CMD ["/usr/local/bin/xray", "run", "-config", "/app/config.json"]
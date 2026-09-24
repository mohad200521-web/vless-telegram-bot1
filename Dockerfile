FROM ghcr.io/xtls/xray-core:latest

EXPOSE 8080

COPY config.json /usr/local/etc/xray/config.json

CMD ["xray", "run", "-config", "/usr/local/etc/xray/config.json"]
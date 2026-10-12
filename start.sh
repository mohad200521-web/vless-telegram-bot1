
#!/bin/sh
set -e

/usr/local/bin/xray run -config /etc/xray/config.json &
exec python /app/bot.py

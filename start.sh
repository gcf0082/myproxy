#!/bin/bash
# Start myproxy HTTP/HTTPS proxy server

PORT=${1:-8080}
CONF=${2:-config.yaml}

echo "Starting myproxy on port $PORT..."
echo "Config: $CONF"
echo "Make sure to install the mitmproxy CA certificate."
echo "Visit http://mitm.it to download certificates."
echo ""

mitmdump --listen-port "$PORT" --set confpath="$CONF" --set ssl_insecure=true -s addon.py
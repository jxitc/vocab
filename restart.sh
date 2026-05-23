#!/bin/bash
# Remote restart — called by deploy.sh on the server
set -e
cd "$(dirname "$0")"

echo "→ Killing old server..."
kill $(lsof -t -i :5001) 2>/dev/null || true
sleep 1

echo "→ Starting server..."
source venv/bin/activate
pip install -r requirements.txt -q
cd src
nohup python server.py > /tmp/vocab-server.log 2>&1 &

echo "✅ Server restarted (PID $!)"

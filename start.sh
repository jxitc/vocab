#!/bin/bash
# Vocab in News — production start script
set -e

cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d venv ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q

cd src
echo "Starting Vocab in News on http://0.0.0.0:5001"
python server.py

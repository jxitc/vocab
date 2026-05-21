#!/bin/bash
# Vocab in News — production start script
set -e

cd "$(dirname "$0")/src"

# Install deps if needed
pip3 install -r ../requirements.txt -q

echo "Starting Vocab in News on http://0.0.0.0:5001"
python3 server.py

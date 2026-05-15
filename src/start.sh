#!/bin/bash
# Start the Vocab in News web server (Iteration 0)

cd "$(dirname "$0")"

echo "Starting Vocab in News server..."
echo "Open http://localhost:5001 in your browser"
echo ""

python3 server.py

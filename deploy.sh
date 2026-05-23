#!/bin/bash
# Deploy Vocab in News to remote server
# Usage: ./deploy.sh [host]  (default: 188.166.172.192)
set -e

HOST="${1:-188.166.172.192}"
REMOTE_DIR="~/vocab"

echo "🚀 Deploying to $HOST..."

echo "→ Pushing to GitHub..."
git push

echo "→ SSH: git pull + restart..."
ssh "$HOST" "cd $REMOTE_DIR && git pull && bash restart.sh"

echo "✅ Deployed! http://$HOST:5001"

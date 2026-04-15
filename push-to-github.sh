#!/bin/bash
# push-to-github.sh - Push changes to GitHub
# Run this with your GitHub token to push the fixes

cd /home/dinesh/.openclaw/workspace/kids-channel-auto

echo "Pushing Kids Channel Auto fixes to GitHub..."
echo ""

# Check if token is provided
if [ -z "$1" ]; then
    echo "Usage: ./push-to-github.sh YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"
    echo ""
    echo "To get a token:"
    echo "1. Go to https://github.com/settings/tokens"
    echo "2. Click 'Generate new token (classic)'"
    echo "3. Select 'repo' scope (full control)"
    echo "4. Generate and copy the token"
    exit 1
fi

TOKEN="$1"
REPO="vgdine69-pixel/kids-channel-auto"

# Push the changes
git push https://x-access-token:${TOKEN}@github.com/${REPO}.git master

echo ""
echo "✅ Code pushed successfully!"
echo ""
echo "Now go to: https://github.com/${REPO}/actions"
echo "Click 'Run workflow' to test it!"
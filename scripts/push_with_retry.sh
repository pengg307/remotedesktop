#!/bin/bash
# Git Push with Auto-Retry Script
# For unstable network connections (China -> GitHub)

REPO_DIR="${1:-.}"
MAX_RETRIES=10
RETRY_DELAY=10  # seconds between retries

echo "=================================="
echo "Git Push Auto-Retry Script"
echo "=================================="
echo "Repository: $REPO_DIR"
echo "Max retries: $MAX_RETRIES"
echo "Retry delay: ${RETRY_DELAY}s"
echo ""

cd "$REPO_DIR" || exit 1

# Check if there are changes to push
echo "Checking git status..."
git status --short
echo ""

# Try to push with retry logic
for i in $(seq 1 $MAX_RETRIES); do
    echo "[$i/$MAX_RETRIES] Attempting to push..."
    
    if git push origin main 2>&1; then
        echo ""
        echo "=================================="
        echo "✓ Push successful!"
        echo "=================================="
        exit 0
    fi
    
    # Check if error is network-related
    if git push origin main 2>&1 | grep -qi "connection\|timeout\|reset\|failed"; then
        echo "⚠ Network error detected"
    fi
    
    if [ $i -lt $MAX_RETRIES ]; then
        echo "Waiting ${RETRY_DELAY}s before retry..."
        sleep $RETRY_DELAY
    fi
done

echo ""
echo "=================================="
echo "✗ Failed after $MAX_RETRIES attempts"
echo "=================================="
echo ""
echo "Suggestions:"
echo "1. Check your network connection"
echo "2. Try using a VPN/proxy"
echo "3. Wait a few minutes and try again"
echo "4. Consider using SSH instead of HTTPS"
exit 1

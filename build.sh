#!/usr/bin/env bash
set -e

echo "=== Current directory: $PWD ==="

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Installing Playwright Chromium browser ==="
# Install to /opt/render/project/src (the project root, which persists)
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/pw-browsers
mkdir -p /opt/render/project/src/pw-browsers
python -m playwright install chromium

echo "=== Checking browser installation ==="
ls -la /opt/render/project/src/pw-browsers/
find /opt/render/project/src/pw-browsers -type f -name "*chrome*" | head -3

echo "=== Verifying Playwright can launch browser ==="
PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/pw-browsers python -c "
from playwright.sync_api import sync_playwright
p = sync_playwright().start()
b = p.chromium.launch(headless=True)
print('Browser launched successfully!')
b.close()
p.stop()
"

echo "=== Build complete ==="

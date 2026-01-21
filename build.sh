#!/usr/bin/env bash
set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Installing Playwright Chromium browser ==="
# Install to project directory (persisted between build and runtime)
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.browsers
mkdir -p $PLAYWRIGHT_BROWSERS_PATH
echo "Installing browsers to: $PLAYWRIGHT_BROWSERS_PATH"
playwright install chromium

echo "=== Browser installed to: ==="
ls -la $PLAYWRIGHT_BROWSERS_PATH
find $PLAYWRIGHT_BROWSERS_PATH -name "chrome*" -type f 2>/dev/null | head -5

echo "=== Verifying Playwright installation ==="
PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.browsers python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=True); b.close(); p.stop(); print('Playwright browser test: OK')"

echo "=== Build complete ==="

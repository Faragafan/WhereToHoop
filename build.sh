#!/usr/bin/env bash
set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Installing Playwright Chromium browser ==="
# Install to project directory (persisted between build and runtime)
export PLAYWRIGHT_BROWSERS_PATH=$PWD/.browsers
mkdir -p $PLAYWRIGHT_BROWSERS_PATH
playwright install chromium

echo "=== Browser installed to: $PLAYWRIGHT_BROWSERS_PATH ==="
ls -la $PLAYWRIGHT_BROWSERS_PATH

echo "=== Verifying Playwright installation ==="
PLAYWRIGHT_BROWSERS_PATH=$PWD/.browsers python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"

echo "=== Build complete ==="

#!/usr/bin/env bash
set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Installing Playwright Chromium browser ==="
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
playwright install chromium

echo "=== Verifying Playwright installation ==="
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"

echo "=== Build complete ==="

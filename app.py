"""                                                                                                                                                          
Basketball Court Availability Dashboard
A Flask web application to visualize basketball court availability.
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from pathlib import Path
from datetime import datetime
import sys
import threading
import traceback

# Import scraper functions
from scraper import scrape_calendar_parallel, save_data, DATA_FILE

app = Flask(__name__)

# Thread lock to prevent concurrent scrapes
scrape_lock = threading.Lock()
scrape_in_progress = False
last_scrape_success = None
last_scrape_error = None


def load_data():
    """Load availability data from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"venues": {}, "last_updated": None}


def run_scraper_background():
    """Run the parallel scraper in background and save data."""
    global scrape_in_progress, last_scrape_success, last_scrape_error
    try:
        print("🔄 Starting scraper...")
        all_venue_data = scrape_calendar_parallel(headless=True)
        save_data(all_venue_data)
        print("✅ Scraper completed!")
        last_scrape_success = datetime.now().isoformat()
        last_scrape_error = None
        return True
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"❌ Scraper error: {error_msg}")
        last_scrape_error = str(e)
        return False
    finally:
        with scrape_lock:
            scrape_in_progress = False


@app.route('/')
def index():
    """Main dashboard page - loads instantly with cached data."""
    # Auto-scrape on first visit if no data exists
    if not DATA_FILE.exists():
        print("🔄 No data found - triggering initial scrape...")
        global scrape_in_progress
        with scrape_lock:
            if not scrape_in_progress:
                scrape_in_progress = True
                thread = threading.Thread(target=run_scraper_background, daemon=True)
                thread.start()
    
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint for Render."""
    return jsonify({"status": "ok"}), 200


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """API endpoint to trigger a data refresh in background."""
    global scrape_in_progress
    
    with scrape_lock:
        if scrape_in_progress:
            return jsonify({
                "status": "already_running", 
                "message": "Scrape already in progress"
            }), 202
        scrape_in_progress = True
    
    # Run scraper in a background thread
    thread = threading.Thread(target=run_scraper_background, daemon=True)
    thread.start()
    
    return jsonify({
        "status": "started", 
        "message": "Refresh started in background"
    })


@app.route('/api/refresh/status')
def refresh_status():
    """Check if a refresh is currently running with detailed status."""
    return jsonify({
        "in_progress": scrape_in_progress,
        "last_success": last_scrape_success,
        "last_error": last_scrape_error
    })

@app.route('/api/data')
def get_data():
    """API endpoint to get all availability data."""
    data = load_data()
    return jsonify(data)


@app.route('/api/venues')
def get_venues():
    """API endpoint to get list of venues."""
    data = load_data()
    venues = []
    for venue_id, venue_data in data.get("venues", {}).items():
        venues.append({
            "id": venue_id,
            "name": venue_data.get("name", venue_id),
            "days": list(venue_data.get("days", {}).keys())
        })
    return jsonify(venues)


@app.route('/api/data/<venue_id>')
def get_venue_data(venue_id):
    """API endpoint to get data for a specific venue."""
    data = load_data()
    
    if venue_id in data.get("venues", {}):
        return jsonify(data["venues"][venue_id])
    
    return jsonify({"error": "Venue not found"}), 404


@app.route('/api/data/<venue_id>/<date>')
def get_venue_date_data(venue_id, date):
    """API endpoint to get data for a specific venue and date."""
    data = load_data()
    
    if venue_id in data.get("venues", {}):
        venue_data = data["venues"][venue_id]
        if date in venue_data.get("days", {}):
            return jsonify(venue_data["days"][date])
    
    return jsonify({"error": "Data not found"}), 404


if __name__ == '__main__':
    print("🏀 Basketball Court Availability Dashboard")
    print("=" * 50)
    print("Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    # use_reloader=False prevents Flask from restarting mid-scrape
    app.run(debug=True, port=5000, use_reloader=False)

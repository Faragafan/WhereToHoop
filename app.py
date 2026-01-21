"""                                                                                                                                                          
Basketball Court Availability Dashboard
A Flask web application to visualize basketball court availability.
"""

from flask import Flask, render_template, jsonify, request
import json
from pathlib import Path
from datetime import datetime
import sys

# Import scraper functions
from scraper import scrape_calendar_parallel, save_data

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "data" / "availability.json"


def load_data():
    """Load availability data from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"venues": {}, "last_updated": None}


def run_scraper():
    """Run the parallel scraper and save data."""
    try:
        all_venue_data = scrape_calendar_parallel(headless=True, max_workers=6)
        save_data(all_venue_data)
        return True
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        return False


@app.route('/')
def index():
    """Main dashboard page - scrapes all venues in parallel then renders."""
    run_scraper()
    return render_template('index.html')


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """API endpoint to trigger a data refresh."""
    success = run_scraper()
    if success:
        return jsonify({"status": "success", "message": "Data refreshed"})
    else:
        return jsonify({"status": "error", "message": "Scrape failed"}), 500
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

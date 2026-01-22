# 🏀 Where to Hoop Bro

A real-time basketball court availability tracker for Melbourne recreation centres.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.40+-purple.svg)

## What is this?

Tired of showing up to the courts only to find them fully booked? **Where to Hoop** scrapes availability data from multiple Melbourne recreation centres and displays it in a clean, mobile-friendly dashboard.

### Venues Tracked

| Venue | Location |
|-------|----------|
| Aqualink | Box Hill |
| Boroondara Sports Complex | Balwyn |
| Carlton Baths | Carlton |
| Narrandjeri Stadium | Thornbury |
| Macleod Recreation & Fitness Centre| Macleod |
| Sportslink | Vermont South |

## Features

- 🕐 **Real-time clock** - See current time and where is available right now
- 📱 **Mobile-friendly** - Check availability from your phone
- 📅 **Multi-day view** - Check availability for the next 5-7 days
- 🔍 **Filters** - Show all slots, available only, or slots with 3+ spots
- ⚡ **Instant loading** - Dashboard loads immediately from cached data
- 🔄 **RESTful API** - Access venue data programmatically via JSON endpoints
- 🚀 **Parallel scraping** - Fast data collection using concurrent browser instances

## Screenshots

The dashboard shows:
- Venues available right now
- Venues with availability in the next 2 hours
- Detailed time slots for each venue

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/Faragafan/WhereToHoop.git
   cd WhereToHoop
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   python -m playwright install chromium
   ```

5. **Run the scraper (to populate initial data)**
   ```bash
   python scraper.py
   ```

6. **Run the app**
   ```bash
   python app.py
   ```

7. **Open in browser**
   ```
   http://localhost:5000
   ```

## Environment Variables

The app supports the following environment variables:

- `DATA_DIR`: Directory for storing scraped data (default: `./data`)
- `MAX_WORKERS`: Maximum parallel workers for scraping (default: `3`, recommended for cloud deployments)

## How It Works

1. **Background scraping**: Data is pre-scraped in parallel using ThreadPoolExecutor (configurable via `MAX_WORKERS` environment variable, default: 3)
2. **Cached data**: Scraped data is saved to `data/availability.json` with timestamps
3. **Instant loading**: The dashboard loads instantly from cached data - no waiting for scrapes
4. **Multiple APIs**: RESTful API endpoints (`/api/data`, `/api/venues`, `/api/data/<venue_id>`) for flexible data access
5. **Auto-refresh**: Can be set up with GitHub Actions cron jobs for automatic data updates

## Tech Stack

- **Backend**: Flask (Python)
- **Scraping**: Playwright (headless Chromium) with parallel execution via ThreadPoolExecutor
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Data Storage**: JSON file cache with timestamp tracking
- **Deployment**: Render.com with persistent disk support
- **CI/CD**: GitHub Actions compatible for automated scraping

## Deployment

This app is configured for deployment on [Render.com](https://render.com):

1. Push to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repo
4. Set start command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`
5. **(Optional)** Add a persistent disk mounted at `/data` and set `DATA_DIR=/data` environment variable
6. **(Recommended)** Set up a cron job or GitHub Action to run `scraper.py` periodically to refresh data
7. Deploy!

## API Endpoints

The app provides several RESTful endpoints:

- `GET /` - Main dashboard UI
- `GET /health` - Health check endpoint
- `GET /api/data` - Full dataset (all venues with timestamps)
- `GET /api/venues` - List of all venues with available dates
- `GET /api/data/<venue_id>` - Data for a specific venue
- `GET /api/data/<venue_id>/<date>` - Data for a specific venue and date (YYYY-MM-DD format)

## Project Structure

```
whereToHoop/
├── app.py              # Flask web application with API endpoints
├── scraper.py          # Playwright parallel scraping logic
├── requirements.txt    # Python dependencies
├── Procfile            # Deployment config
├── Dockerfile          # Docker container config
├── render.yaml         # Render.com config
├── data/
│   └── availability.json   # Scraped data cache with timestamps
└── templates/
    └── index.html      # Dashboard frontend (Bootstrap 5)
```

## Usage Examples

### Running the scraper manually
```bash
python scraper.py
```

### Accessing API data
```bash
# Get all data
curl http://localhost:5000/api/data

# Get specific venue
curl http://localhost:5000/api/data/aqualink

# Get specific date
curl http://localhost:5000/api/data/aqualink/2026-01-23
```

## Contributing

Found a bug or want to add a venue? PRs welcome!

## Disclaimer

This project scrapes publicly available booking calendars for personal use. Please be respectful of the recreation centres' websites and don't abuse the scraping functionality.

## License

MIT

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

5. **Run the app**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

## How It Works

1. When you open the website, it launches 6 headless Chrome browsers in parallel
2. Each browser scrapes a different venue's booking calendar
3. Data is parsed and saved to `data/availability.json`
4. The dashboard renders the combined data with real-time filtering

## Tech Stack

- **Backend**: Flask (Python)
- **Scraping**: Playwright (headless Chromium)
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Deployment**: Render.com

## Deployment

This app is configured for deployment on [Render.com](https://render.com):

1. Push to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repo
4. Set start command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`
5. Deploy!

## Project Structure

```
whereToHoop/
├── app.py              # Flask application
├── scraper.py          # Playwright scraping logic
├── requirements.txt    # Python dependencies
├── Procfile            # Deployment config
├── render.yaml         # Render.com config
├── data/
│   └── availability.json   # Scraped data cache
└── templates/
    └── index.html      # Dashboard frontend
```

## Contributing

Found a bug or want to add a venue? PRs welcome!

## Disclaimer

This project scrapes publicly available booking calendars for personal use. Please be respectful of the recreation centres' websites and don't abuse the scraping functionality.

## License

MIT

from playwright.sync_api import sync_playwright
import time
import json
import re
import os
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Define venues to scrape
VENUES = {
    "boroondara": {
        "name": "Boroondara Leisure",
        "url": "https://boroondaraleisure.perfectgym.com.au/ClientPortal2/ClubZoneOccupancyCalendar/3a1132fc5"
    },
    "darebin": {
        "name": "Darebin",
        "url": "https://darebin.perfectgym.com.au/ClientPortal2/ClubZoneOccupancyCalendar/09869a3c4"
    },
    "sportslink": {
        "name": "Sportslink",
        "url": "https://aqualink.perfectgym.com.au/ClientPortal2/ClubZoneOccupancyCalendar/3ce734397"
    },
    "carltonbaths": {
        "name": "Carlton Baths",
        "url": "https://activemelbourne-ymca.perfectgym.com/ClientPortal2/ClubZoneOccupancyCalendar/894234c91"
    },
    "macleod": {
        "name": "Macleod",
        "url": "https://mrfc.perfectgym.com.au/ClientPortal2/ClubZoneOccupancyCalendar/36b6925a1"
    },
    "aqualink": {
        "name": "Aqualink",
        "url": "https://aqualink.perfectgym.com.au/ClientPortal2/ClubZoneOccupancyCalendar/6b1539a68?_gl=1*13d1e4w*_gcl_au*NDUyNjkxMzQ0LjE3NjgxMDM1NDQ.*_ga*OTk4NzY0NjA1LjE3NjgxMDM1NDM.*_ga_H5VPG63HEP*czE3Njg5OTEwNDAkbzIkZzAkdDE3Njg5OTEwNDAkajYwJGwwJGgyMDczMjk5NzA."
    }
}

# Support persistent data directory (for Render persistent disk)
DATA_DIR = os.environ.get('DATA_DIR', str(Path(__file__).parent / "data"))
DATA_FILE = Path(DATA_DIR) / "availability.json"

# Cloud-friendly concurrency (default 1 for Render free tier)
DEFAULT_MAX_WORKERS = int(os.environ.get('MAX_WORKERS', '1'))


def parse_availability(text):
    """Parse availability text like '3 / 5 AVAILABLE' into (available, max)."""
    match = re.search(r'(\d+)\s*/\s*(\d+)', text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0


def parse_time_to_minutes(time_str):
    """Convert time string to minutes since midnight for comparison."""
    try:
        for fmt in ["%I:%M %p", "%H:%M", "%I:%M%p"]:
            try:
                dt = datetime.strptime(time_str.strip(), fmt)
                return dt.hour * 60 + dt.minute
            except ValueError:
                continue
    except Exception:
        pass
    return 0


def parse_time_slot(time_str):
    """Parse time string into sortable 24h format."""
    try:
        for fmt in ["%I:%M %p", "%H:%M", "%I:%M%p"]:
            try:
                return datetime.strptime(time_str.strip(), fmt).strftime("%H:%M")
            except ValueError:
                continue
    except Exception:
        pass
    return time_str


def split_into_days(slots, start_date=None):
    """
    Split a flat list of slots into separate days.
    A new day starts when the time resets (current time <= previous time).
    """
    if start_date is None:
        start_date = datetime.now().date()
    
    days = {}
    current_day_slots = []
    current_date = start_date
    prev_minutes = -1
    
    for slot in slots:
        current_minutes = parse_time_to_minutes(slot['time_slot'])
        
        # Detect day boundary: time reset (e.g., 8:30 PM -> 5:30 AM)
        if current_minutes <= prev_minutes and current_day_slots:
            # Save the completed day
            date_str = current_date.strftime("%Y-%m-%d")
            days[date_str] = current_day_slots
            current_day_slots = []
            current_date += timedelta(days=1)
        
        current_day_slots.append(slot)
        prev_minutes = current_minutes
    
    # Don't forget the last day
    if current_day_slots:
        date_str = current_date.strftime("%Y-%m-%d")
        days[date_str] = current_day_slots
    
    return days


def scrape_venue(page, url, venue_name, headless=False):
    """Scrape a single venue and return days data."""
    page.goto(url, timeout=60000)
    
    # Wait for calendar blocks to appear
    page.wait_for_selector("div[class*='facility-calendar-block']", timeout=60000)
    
    # Small delay to ensure all blocks are rendered
    page.wait_for_timeout(1000)

    blocks = page.query_selector_all("div[class*='facility-calendar-block']")

    all_slots = []

    for block in blocks:
        text = block.inner_text().strip()
        lines = text.split("\n")
        
        if len(lines) < 2:
            continue

        time_slot = lines[0].strip()
        availability_text = lines[1].strip()
        
        # Check if it's available or not
        if "NOT AVAILABLE" in availability_text.upper():
            available = 0
            max_slots = 5  # Default max
        else:
            available, max_slots = parse_availability(availability_text)
        
        time_24h = parse_time_slot(time_slot)

        all_slots.append({
            "time_slot": time_slot,
            "time_24h": time_24h,
            "availability_text": availability_text,
            "available": available,
            "max_slots": max_slots
        })

    # Split into days
    days_data = split_into_days(all_slots)
    return days_data


def scrape_venue_standalone(venue_id, venue_info, headless=True):
    """Scrape a single venue in its own browser context (for parallel execution)."""
    with sync_playwright() as p:
        # Container-friendly browser launch args
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer'
            ]
        )
        page = browser.new_page()
        try:
            days_data = scrape_venue(page, venue_info["url"], venue_info["name"], headless)
            return venue_id, {
                "name": venue_info["name"],
                "days": days_data
            }
        except Exception as e:
            print(f"❌ Error scraping {venue_info['name']}: {e}")
            return venue_id, {
                "name": venue_info["name"],
                "days": {},
                "error": str(e)
            }
        finally:
            browser.close()


def scrape_calendar_parallel(headless=True, venues=None, max_workers=None):
    """Scrape all venues in parallel for much faster execution."""
    if venues is None:
        venues = VENUES
    
    if max_workers is None:
        max_workers = DEFAULT_MAX_WORKERS
    
    all_venue_data = {}
    completed_count = 0
    total_venues = len(venues)
    start_time = time.time()
    lock = threading.Lock()
    
    print(f"\n{'='*60}")
    print(f"🏀 SCRAPING {total_venues} VENUES (max_workers={max_workers})")
    print(f"{'='*60}")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(scrape_venue_standalone, venue_id, venue_info, headless): (venue_id, venue_info)
            for venue_id, venue_info in venues.items()
        }
        
        for future in as_completed(futures):
            venue_id, venue_data = future.result()
            all_venue_data[venue_id] = venue_data
            
            with lock:
                completed_count += 1
                days_count = len(venue_data.get('days', {}))
                status = "✅" if days_count > 0 else "⚠️"
                print(f"  {status} [{completed_count}/{total_venues}] {venue_data['name']:<20} ({days_count} days)")
    
    elapsed = time.time() - start_time
    print(f"{'='*60}")
    print(f"⚡ Done in {elapsed:.1f}s | {total_venues} venues scraped")
    print(f"{'='*60}\n")
    
    return all_venue_data


def scrape_calendar(headless=False, venues=None):
    """Scrape basketball court availability from all venues."""
    if venues is None:
        venues = VENUES
    
    all_venue_data = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=0 if headless else 50)
        page = browser.new_page()

        for venue_id, venue_info in venues.items():
            try:
                days_data = scrape_venue(page, venue_info["url"], venue_info["name"], headless)
                all_venue_data[venue_id] = {
                    "name": venue_info["name"],
                    "days": days_data
                }
            except Exception as e:
                print(f"❌ Error scraping {venue_info['name']}: {e}")
                all_venue_data[venue_id] = {
                    "name": venue_info["name"],
                    "days": {},
                    "error": str(e)
                }

        print("\nDone. Browser will close in 1 second...")
        time.sleep(1)
        browser.close()

    return all_venue_data


def save_data(all_venue_data):
    """Save scraped data to JSON file."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "venues": all_venue_data,
        "last_updated": datetime.now().isoformat()
    }
    
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    total_days = sum(len(v.get("days", {})) for v in all_venue_data.values())
    print(f"💾 Saved: {len(all_venue_data)} venues, {total_days} days → {DATA_FILE.name}")
    return data


def load_data():
    """Load scraped data from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"venues": {}, "last_updated": None}


def print_table(all_venue_data):
    """Print a formatted table to console."""
    if not all_venue_data:
        print("No data found.")
        return
    
    for venue_id, venue_data in all_venue_data.items():
        print(f"\n{'#' * 60}")
        print(f"📍 {venue_data['name']}")
        print(f"{'#' * 60}")
        
        days_data = venue_data.get("days", {})
        
        for date_str, slots in sorted(days_data.items()):
            print(f"\n{'=' * 50}")
            print(f"📅 {date_str}")
            print(f"{'=' * 50}")
            print(f"{'Time Slot':<20} {'Available':<12} {'Status'}")
            print("-" * 50)
            
            for slot in slots:
                available = slot['available']
                max_slots = slot['max_slots']
                
                if available == 0:
                    status = "❌ Full"
                elif available >= 3:
                    status = "✅ Good"
                else:
                    status = "⚠️ Limited"
                
                print(f"{slot['time_slot']:<20} {available}/{max_slots:<10} {status}")


if __name__ == "__main__":
    all_venue_data = scrape_calendar()
    print_table(all_venue_data)
    save_data(all_venue_data)

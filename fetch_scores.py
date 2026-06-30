import json
import requests
import sys
import time

SCHEDULE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=20260611-20260719&limit=200"
LIVE_URL_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def fetch_data(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.json().get("events", [])
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def main():
    print("Fetching World Cup schedule...")
    schedule_events = fetch_data(SCHEDULE_URL)
    
    # Cache-busting URL generation
    current_timestamp = int(time.time())
    live_url = f"{LIVE_URL_BASE}?_={current_timestamp}"
    
    print(f"Fetching LIVE updates (Cache-Busted: {live_url})...")
    live_events = fetch_data(live_url)
    
    live_dict = { event["id"]: event for event in live_events }

    matches = []

    for event in schedule_events:
        event_id = event.get("id")
        
        if event_id in live_dict:
            event = live_dict[event_id]
            
        try:
            competition = event.get("competitions", [{}])[0]
            competitors = competition.get("competitors", [])

            if len(competitors) < 2:
                continue

            home_team_data = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
            away_team_data = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])

            home_name = home_team_data.get("team", {}).get("name", "TBD")
            away_name = away_team_data.get("team", {}).get("name", "TBD")

            # --- BOSNIA NAME NORMALIZATION FIX ---
            if home_name == "Bosnia-Herzegovina":
                home_name = "Bosnia & Herzegovina"
            if away_name == "Bosnia-Herzegovina":
                away_name = "Bosnia & Herzegovina"

            status_obj = event.get("status", {}).get("type", {})
            state = status_obj.get("state", "pre")
            status_name = status_obj.get("name", "")
            
            # --- EXTRACT STAGE/ROUND NAME ---
            notes = competition.get("notes", [])
            stage_name = notes[0].get("headline", "") if notes else ""
            
            # --- EXTRACT PENALTY SHOOTOUTS ---
            home_pen = home_team_data.get("shootoutScore")
            away_pen = away_team_data.get("shootoutScore")
            penalties = [int(home_pen), int(away_pen)] if home_pen is not None and away_pen is not None else None
            
            score = None
            status = "NS"

            if state == "post":
                status = "FT"
                score = [int(home_team_data.get("score", 0)), int(away_team_data.get("score", 0))]
            elif state == "in":
                status = "LIVE"
                score = [int(home_team_data.get("score", 0)), int(away_team_data.get("score", 0))]
            elif status_name in ["STATUS_POSTPONED", "STATUS_CANCELED"]:
                status = "CANCELED"

            venue = "TBD"
            venue_data = competition.get("venue", {})
            if "address" in venue_data:
                venue = venue_data["address"].get("city", "TBD")

            matches.append({
                "t1": home_name,
                "t2": away_name,
                "utc": event.get("date"),
                "v": venue,
                "s": score,
                "p": penalties,
                "status": status,
                "stage": stage_name
            })
            
        except Exception as e:
            continue

    with open("live_scores.json", "w") as f:
        json.dump(matches, f, indent=2)

    print(f"Successfully saved {len(matches)} matches!")

if __name__ == "__main__":
    main()

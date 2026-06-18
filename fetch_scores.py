import json
import requests
import sys

# 1. The calendar URL (gives us all 104 matches, but heavily cached)
SCHEDULE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=20260611-20260719&limit=200"

# 2. The live URL (gives us ONLY today's matches, but updates instantly)
LIVE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"

def fetch_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get("events", [])
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def main():
    print("Fetching World Cup schedule...")
    schedule_events = fetch_data(SCHEDULE_URL)
    
    print("Fetching LIVE updates...")
    live_events = fetch_data(LIVE_URL)
    
    # Create a dictionary of today's live events so we can easily find them
    live_dict = { event["id"]: event for event in live_events }

    matches = []

    for event in schedule_events:
        event_id = event.get("id")
        
        # THE MAGIC: If this match is happening today, swap the stale calendar data with the fresh live data!
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

            status_obj = event.get("status", {}).get("type", {})
            state = status_obj.get("state", "pre")
            status_name = status_obj.get("name", "")
            
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
                "status": status
            })
            
        except Exception as e:
            continue

    with open("live_scores.json", "w") as f:
        json.dump(matches, f, indent=2)

    print(f"Successfully saved {len(matches)} matches!")

if __name__ == "__main__":
    main()

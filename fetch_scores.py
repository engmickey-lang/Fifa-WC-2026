import json
import requests
import sys

URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=20260611-20260719&limit=200"

def main():
    print("Fetching World Cup data from ESPN...")
    
    # 1. Safely handle the internet request
    try:
        response = requests.get(URL)
        response.raise_for_status() # Catches 404s or server errors
        data = response.json()
    except Exception as e:
        print(f"Error fetching from ESPN: {e}")
        sys.exit(1)

    matches = []

    # 2. Safely loop through events, skipping entirely broken ones
    for event in data.get("events", []):
        try:
            competition = event.get("competitions", [{}])[0]
            competitors = competition.get("competitors", [])

            if len(competitors) < 2:
                continue

            # Safely grab home and away blocks
            home_team_data = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
            away_team_data = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])

            # Safely extract names (defaults to TBD if ESPN leaves it blank)
            home_name = home_team_data.get("team", {}).get("name", "TBD")
            away_name = away_team_data.get("team", {}).get("name", "TBD")

            status_name = event.get("status", {}).get("type", {}).get("name", "STATUS_SCHEDULED")

            score = None
            status = "NS"

            # Parse the match status safely
            if status_name in ["STATUS_FINAL", "STATUS_FULL_TIME"]:
                status = "FT"
                score = [int(home_team_data.get("score", 0)), int(away_team_data.get("score", 0))]
            elif status_name in ["STATUS_IN_PROGRESS", "STATUS_HALFTIME", "STATUS_END_PERIOD"]:
                status = "LIVE"
                score = [int(home_team_data.get("score", 0)), int(away_team_data.get("score", 0))]
            elif status_name in ["STATUS_POSTPONED", "STATUS_CANCELED"]:
                status = "CANCELED"

            # Safely extract the venue city
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
            # If a single match is heavily corrupted, skip it but keep running the rest!
            print(f"Skipping a corrupted match entry: {e}")
            continue

    # 3. Save the data
    with open("live_scores.json", "w") as f:
        json.dump(matches, f, indent=2)

    print(f"Successfully saved {len(matches)} matches!")

if __name__ == "__main__":
    main()

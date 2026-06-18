import json
import requests
import sys

URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=20260611-20260719&limit=200"

def main():
    print("Fetching World Cup data from ESPN...")
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching from ESPN: {e}")
        sys.exit(1)

    matches = []

    for event in data.get("events", []):
        try:
            competition = event.get("competitions", [{}])[0]
            competitors = competition.get("competitors", [])

            if len(competitors) < 2:
                continue

            home_team_data = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
            away_team_data = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])

            home_name = home_team_data.get("team", {}).get("name", "TBD")
            away_name = away_team_data.get("team", {}).get("name", "TBD")

            # Get the exact state of the game (pre, in, post)
            status_obj = event.get("status", {}).get("type", {})
            state = status_obj.get("state", "pre")
            
            score = None
            status = "NS"

            # Universally check if the game is finished, live, or upcoming
            if state == "post":
                status = "FT"
                score = [int(home_team_data.get("score", 0)), int(away_team_data.get("score", 0))]
            elif state == "in":
                status = "LIVE"
                score = [int(home_team_data.get("score", 0)), int(away_team_data.get("score", 0))]
            elif status_obj.get("name") in ["STATUS_POSTPONED", "STATUS_CANCELED"]:
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
            print(f"Skipping a corrupted match entry: {e}")
            continue

    with open("live_scores.json", "w") as f:
        json.dump(matches, f, indent=2)

    print(f"Successfully saved {len(matches)} matches!")

if __name__ == "__main__":
    main()

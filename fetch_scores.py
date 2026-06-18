import json
import requests

# We ask ESPN for all matches between the start and end dates of the 2026 tournament
URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=20260611-20260719&limit=200"

def main():
    print("Fetching World Cup data from ESPN...")
    response = requests.get(URL)
    data = response.json()
    
    matches = []
    
    for event in data.get("events", []):
        competition = event["competitions"][0]
        competitors = competition["competitors"]
        
        # ESPN gives us home/away teams
        home_team = next((c for c in competitors if c["homeAway"] == "home"), competitors[0])
        away_team = next((c for c in competitors if c["homeAway"] == "away"), competitors[1])
        
        status_name = event["status"]["type"]["name"]
        
        score = None
        status = "NS"
        
        # Translate ESPN's status to our simple UI status
        if status_name in ["STATUS_FINAL", "STATUS_FULL_TIME"]:
            status = "FT"
            score = [int(home_team.get("score", 0)), int(away_team.get("score", 0))]
        elif status_name in ["STATUS_IN_PROGRESS", "STATUS_HALFTIME"]:
            status = "LIVE"
            score = [int(home_team.get("score", 0)), int(away_team.get("score", 0))]
            
        # Extract the venue city safely
        venue = "TBD"
        if "venue" in competition and "address" in competition["venue"]:
            venue = competition["venue"]["address"].get("city", "TBD")
            
        matches.append({
            "t1": home_team["team"]["name"],
            "t2": away_team["team"]["name"],
            "utc": event["date"],
            "v": venue,
            "s": score,
            "status": status
        })
        
    with open("live_scores.json", "w") as f:
        json.dump(matches, f, indent=2)
        
    print(f"Successfully saved {len(matches)} matches!")

if __name__ == "__main__":
    main()        # 6. Save only the clean, essential data we care about
        matches.append({
            "t1": teams["home"]["name"],
            "t2": teams["away"]["name"],
            "utc": fixture["date"],       # This is the exact UTC time (fixes your bug!)
            "v": fixture["venue"]["city"] or "TBD",
            "s": score,
            "status": status
        })
        
    # 7. Create a file called live_scores.json and write our clean data into it
    with open("live_scores.json", "w") as f:
        json.dump(matches, f, indent=2)

if __name__ == "__main__":
    main()

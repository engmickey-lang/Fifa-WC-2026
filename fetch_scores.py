import os       # Lets us read the secret key from GitHub
import json     # Lets us save data in the .json format your HTML needs
import requests # The library that goes to the internet and fetches data

# 1. Grab your secret key
API_KEY = os.environ.get("API_SPORTS_KEY")

# 2. Set the exact URL for the FIFA World Cup (League 1, Season 2026)
URL = "https://v3.football.api-sports.io/fixtures?league=1&season=2026"

# 3. Present our "ID badge" (API key) to the server
HEADERS = {"x-apisports-key": API_KEY}

def main():
    # 4. Make the request to API-Sports
    response = requests.get(URL, headers=HEADERS)
    data = response.json()
    
    matches = []
    
    # 5. Loop through every match they give us
    for item in data.get("response", []):
        fixture = item["fixture"]
        teams = item["teams"]
        goals = item["goals"]
        
        # Check if the match is finished, live, or hasn't started (NS)
        status = fixture["status"]["short"]
        score = None
        
        # If the match has started (Not 'NS'), record the goals
        if status != "NS":
            home_g = goals["home"] if goals["home"] is not None else 0
            away_g = goals["away"] if goals["away"] is not None else 0
            score = [home_g, away_g]

        # 6. Save only the clean, essential data we care about
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

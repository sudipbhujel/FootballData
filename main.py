import threading
import webbrowser
import datetime

from flask import Flask, render_template, request

from api import get_data_from_url

app = Flask(__name__)

# Replace with your actual API key
API_KEY = "d4c211a2fcbd4268b66b430969f34fbc"

# Dictionary mapping competition names to IDs
COMPETITIONS = {
    "Premier League": "PL",
    "Bundesliga": "BL1",
    "La Liga": "PD",
    "Serie A": "SA",
    "Ligue 1": "FL1",
}

# Define available seasons
SEASONS = [2021, 2022, 2023]  # Adjust or extend this list as needed

# Football Club Logo List
logo_list = []


def get_competition_standings(competition_id, season):
    """Fetch standings from the football-data API."""
    url = f"https://api.football-data.org/v4/competitions/{competition_id}/standings"
    headers = {"X-Auth-Token": API_KEY}
    params = {"season": season}
    return get_data_from_url(url, headers=headers, params=params)


def get_competition_matches(competition_id, season):
    """Fetch upcoming matches from the football-data API."""
    url = f"https://api.football-data.org/v2/competitions/{competition_id}/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": API_KEY}
    params = {"season": season}
    return get_data_from_url(url, headers=headers, params=params)


def get_completed_matches(competition_id, season):
    """Fetch completed matches from the football-data API."""
    url = f"https://api.football-data.org/v2/competitions/{competition_id}/matches?status=FINISHED"
    headers = {"X-Auth-Token": API_KEY}
    params = {"season": season}
    return get_data_from_url(url, headers=headers, params=params)


def get_club_flags(competition_id, season):
    global logo_list
    url = f"https://cdn.logosports.net/club/fb/list?region={competition_id}"
    logo_list = get_data_from_url(url, {}, {})


def set_logos_to_standings(standings):
    for standing in standings["standings"][0]["table"]:
        standing["team"]["logo"] = get_logo_by_team_name(standing["team"]["name"])


def set_logos_to_matches(matches):
    for match in matches["matches"]:
        match["homeTeam"]["logo"] = get_logo_by_team_name(match["homeTeam"]["name"])
        match["awayTeam"]["logo"] = get_logo_by_team_name(match["awayTeam"]["name"])


def get_logo_by_team_name(name):
    global logo_list
    for logo in logo_list:
        if logo["name"] == name:
            return logo["logo"]
    return ""


def format_date(matches):
    for match in matches["matches"]:
        match["utcDate"] = datetime.datetime.strptime(
            match["utcDate"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%d/%m/%Y %H:%M")


@app.route("/")
def home():
    competition_id = request.args.get(
        "competition_id", "PL"
    )  # Default to Premier League
    season = int(request.args.get("season", "2023"))  # Default to 2023 season

    # get footabll datas
    get_club_flags(competition_id, season)
    standings = get_competition_standings(competition_id, season)
    matches = get_competition_matches(competition_id, season)
    completed_matches = get_completed_matches(competition_id, season)

    # set logo url
    set_logos_to_standings(standings)
    set_logos_to_matches(matches)
    set_logos_to_matches(completed_matches)

    format_date(completed_matches)

    return render_template(
        "index.html",
        competitions=COMPETITIONS,
        selected_competition=competition_id,
        seasons=SEASONS,
        selected_season=season,
        standings=standings,
        matches=matches,
        completed_matches=completed_matches,
    )


def open_browser():
    """Launch the default web browser to the specified URL."""
    webbrowser.open("http://localhost:8000/")


if __name__ == "__main__":
    # Start a new thread to open the browser after a delay
    threading.Timer(1, open_browser).start()

    # Run the Flask application
    app.run(port=8000)

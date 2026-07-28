import requests
from datetime import date


def calculate_age(birth_date):

    # Convert YYYY-MM-DD birthdate into current age.

    birth = date.fromisoformat(birth_date)
    today = date.today()

    age = (
        today.year
        - birth.year
        - ((today.month, today.day) < (birth.month, birth.day))
    )

    return age


def determine_role(pitch_data):

    # Determine whether pitcher is SP or RP.

    if pitch_data is None or pitch_data.empty:
        return "P"

    games = pitch_data["game_pk"].nunique()

    if games == 0:
        return "P"

    games_started = 0

    for _, game in pitch_data.groupby("game_pk"):

        # Sort pitches chronologically within each game.
        sort_columns = [
            column
            for column in [
                "inning",
                "at_bat_number",
                "pitch_number",
            ]
            if column in game.columns
        ]

        if sort_columns:
            game = game.sort_values(sort_columns)

        first_pitch = game.iloc[0]

        if first_pitch["inning"] == 1:
            games_started += 1

    start_percentage = games_started / games

    if start_percentage > 0.60:
        return "SP"

    return "RP"

# Helper function to produce the correct abbreviation
# used to locate the matching logo file.

def get_team_details(current_team):
    team_name = current_team.get("name", "")
    team_abbr = current_team.get("abbreviation", "")

    team_id = current_team.get("id")

    # The player endpoint may return only the current team ID.
    if team_id and (not team_name or not team_abbr):
        team_response = requests.get(
            f"https://statsapi.mlb.com/api/v1/teams/{team_id}",
            timeout=10,
        )

        team_response.raise_for_status()

        teams = team_response.json().get("teams", [])

        if teams:
            team_data = teams[0]

            team_name = team_data.get("name", team_name)
            team_abbr = team_data.get("abbreviation", team_abbr)

    return team_name, team_abbr


def get_player_info(pitcher_id, pitch_data):

    # Hydrate currentTeam so the response includes the player's team ID.

    url = (
        f"https://statsapi.mlb.com/api/v1/people/{pitcher_id}"
        "?hydrate=currentTeam"
    )

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        raise Exception(
            f"Unable to retrieve player info ({response.status_code})"
        )

    data = response.json()["people"][0]

    current_team = data.get("currentTeam", {})

    team_name, team_abbr = get_team_details(current_team)

    info = {
        "name": data["fullName"],

        "throws": data["pitchHand"]["code"],

        "age": calculate_age(data["birthDate"]),

        "height": data["height"],

        "team": team_name,

        "team_abbr": team_abbr,

        "role": determine_role(pitch_data),

        "headshot_url": (
            "https://img.mlbstatic.com/mlb-photos/image/upload/"
            "w_360,d_people:generic:headshot:silo:current.png/"
            f"v1/people/{pitcher_id}/headshot/67/current.png"
        ),
    }

    return info
from datetime import date
import requests

CURRENT_SEASON = date.today().year

# MLB's yearly FIP constant.
# Update this each season when needed.
FIP_CONSTANT = 3.135


def ip_to_decimal(ip_string):
    """
    Convert baseball innings notation to decimal innings.

    "6.0" -> 6.0
    "6.1" -> 6.333333
    "6.2" -> 6.666667
    """

    whole, outs = ip_string.split(".")

    return int(whole) + int(outs) / 3


def calculate_fip(hr, bb, hbp, k, ip):

    if ip == 0:
        return 0.0

    fip = (
        (13 * hr)
        + (3 * (bb + hbp))
        - (2 * k)
    ) / ip + FIP_CONSTANT

    return round(fip, 2)


def get_header_stats(pitcher_id):

    url = (
        f"https://statsapi.mlb.com/api/v1/people/"
        f"{pitcher_id}"
        f"/stats?stats=season"
        f"&group=pitching"
        f"&season={CURRENT_SEASON}"
    )

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    splits = data["stats"][0]["splits"]

    if len(splits) == 0:
        return None

    stats = splits[0]["stat"]

    # ----------------------------
    # Official Season Stats
    # ----------------------------

    games = int(stats["gamesPlayed"])
    starts = int(stats["gamesStarted"])

    ip_display = stats["inningsPitched"]
    ip = ip_to_decimal(ip_display)

    era = float(stats["era"])
    whip = float(stats["whip"])

    strikeouts = int(stats["strikeOuts"])
    walks = int(stats["baseOnBalls"])
    hit_by_pitch = int(stats["hitBatsmen"])
    home_runs = int(stats["homeRuns"])

    batters_faced = int(stats["battersFaced"])

    pitches = int(stats["numberOfPitches"])

    # ----------------------------
    # Calculated Stats
    # ----------------------------

    fip = calculate_fip(home_runs, walks, hit_by_pitch, strikeouts, ip)

    k_pct = round(strikeouts / batters_faced * 100, 1)

    bb_pct = round(walks / batters_faced * 100, 1)

    ip_game = round(ip / games, 1) if games else None

    ip_start = round(ip / starts, 1) if starts else None

    pitches_game = round(pitches / games, 1) if games else None

    pitches_start = round(pitches / starts, 1) if starts else None

    # ----------------------------
    # Header Dictionary
    # ----------------------------

    header = {

        "IP": ip_display,

        "ERA": era,

        "FIP": fip,

        "WHIP": whip,

        "K%": k_pct,

        "BB%": bb_pct,

        "G": games,

        "GS": starts,

        "IP/G": ip_game,

        "IP/GS": ip_start,

        "Pitches/G": pitches_game,

        "Pitches/GS": pitches_start

    }

    return header
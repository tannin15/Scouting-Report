
# ------------------------------------------------
# PLAYER LOOKUP AND DATA COLLECTION FOR TABLE ONE
# ------------------------------------------------

from pybaseball import statcast_pitcher, playerid_lookup
from datetime import datetime, timedelta
from pitch_dictionary import PITCH_INFO
import sys
import unicodedata


# Normalize the imputed name to find in the data

def remove_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

def format_player_name(first, last):
    return (
        f"{first.strip().title()} "
        f"{last.strip().title()}"
    )


# ----------------------------------
# FUNCTION TO LATER CLEAN THE DATA
# ----------------------------------

def clean_pitch_data(pitch_data):
    pitch_data = pitch_data.dropna(
        subset=[
            "pitch_type",
            "release_speed",
            "release_spin_rate",
            "pfx_z",
            "pfx_x",
            "zone"
        ]
    ).copy()

    return pitch_data[pitch_data["pitch_type"].isin(PITCH_INFO)].copy()


    

def get_pitcher_id(full_name):

    # Split the entered name into first and last name.

    name_parts = full_name.strip().split()

    if len(name_parts) < 2:
        raise ValueError(
            "Please enter both a first and last name."
        )

    # Normalize the user-entered name.

    first_name = remove_accents(name_parts[0]).strip().casefold()

    last_name = remove_accents(" ".join(name_parts[1:])).strip().casefold()

    # Use fuzzy=True so accented names and minor spelling
    # variations can still be returned by pybaseball.

    results = playerid_lookup(last_name, first_name, fuzzy=True,)

    # If the full-name search returns nothing, broaden the search.

    if results.empty:

        print(
            "\nExact match not found. "
            "Searching possible matches..."
        )

        results = playerid_lookup(last_name, fuzzy=True,)

    if results.empty:

        results = playerid_lookup("", first_name, fuzzy=True,)

    if results.empty:
        raise ValueError(
            "Pitcher not found. Check spelling."
        )

    results = results.copy()

    # Normalize the names returned by pybaseball too.
    # This lets Sanchez match Sánchez.

    results["normalized_first"] = (
        results["name_first"]
        .fillna("")
        .astype(str)
        .map(remove_accents)
        .str.strip()
        .str.casefold()
    )

    results["normalized_last"] = (
        results["name_last"]
        .fillna("")
        .astype(str)
        .map(remove_accents)
        .str.strip()
        .str.casefold()
    )

    # Prefer exact matches after both sides have been normalized.

    exact_results = results[
        results["normalized_first"].eq(first_name)
        & results["normalized_last"].eq(last_name)
    ].copy()

    if not exact_results.empty:
        results = exact_results

    # Keep only players who debuted in 2000 or later.

    results["mlb_played_first"] = (results["mlb_played_first"].fillna(0).astype(int))

    recent_results = results[results["mlb_played_first"] >= 2000].copy()

    if not recent_results.empty:
        results = recent_results

    # Automatically select the player if only one remains.

    if len(results) == 1:

        selected = results.iloc[0]

        pitcher_id = int(selected["key_mlbam"])

        official_name = format_player_name(selected["name_first"], selected["name_last"],)

        print(f"\nFound: {official_name}" f"(MLBID: {pitcher_id})")

        return pitcher_id, official_name

    # Otherwise display the possible matches.

    print("\nPotential matches found:\n")

    matches = results[
        [
            "name_first",
            "name_last",
            "key_mlbam",
            "mlb_played_first",
            "mlb_played_last",
        ]
    ]

    print(matches.to_string(index=False))

    pitcher_id = int(
        input("\nEnter MLB ID from the list above: ")
    )

    selected_matches = results[
        results["key_mlbam"].astype(int).eq(pitcher_id)
    ]

    if selected_matches.empty:
        raise ValueError(
            "The selected MLB ID was not in the match list."
        )

    selected = selected_matches.iloc[0]

    official_name = format_player_name(
        selected["name_first"],
        selected["name_last"],
    )

    return pitcher_id, official_name

# -----------------------------
# DOWNLOAD AND PREPARE DATA
# -----------------------------


def get_pitcher_data(search_name):

    pitcher_id, official_name = get_pitcher_id(search_name)

    # -----------------------------
    # SETTINGS
    # -----------------------------

    season_start = "2026-03-25"
    season_end = datetime.today().strftime("%Y-%m-%d")


    # -----------------------------
    # PULL SEASON DATA
    # -----------------------------

    pitch_data = statcast_pitcher(
        start_dt=season_start,
        end_dt=season_end,
        player_id=pitcher_id
    )

    # Stop if no Statcast pitching data is found
    if pitch_data.empty:
        print(f"\nNo Statcast pitching data found for {official_name}.")
        sys.exit()


    # Last 30 days data

    today = datetime.today()
    start_30 = today - timedelta(days=30)

    recent_data = statcast_pitcher(
        start_dt=start_30.strftime("%Y-%m-%d"),
        end_dt=today.strftime("%Y-%m-%d"),
        player_id=pitcher_id
    )

    # ----------------
    # CLEAN THE DATA
    # ----------------

    pitch_data = clean_pitch_data(pitch_data)
    recent_data = clean_pitch_data(recent_data)

    # -----------------------------
    # MOVEMENT CONVERSION
    # -----------------------------

    for df in (pitch_data, recent_data):

        df["IVB_inches"] = df["pfx_z"] * 12

        # Positive = arm side
        df["HB_inches"] = -df["pfx_x"] * 12



    return pitcher_id, official_name, pitch_data, recent_data



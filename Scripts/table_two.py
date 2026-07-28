import numpy as np
import pandas as pd
from pitch_dictionary import PITCH_INFO


FIRST_PITCH_STRIKES = [
    "called_strike",
    "swinging_strike",
    "swinging_strike_blocked",
    "foul",
    "foul_tip",
    "foul_bunt",
    "missed_bunt",
    "bunt_foul_tip",
    "hit_into_play",
    "hit_into_play_no_out",
    "hit_into_play_score"
]

CSW_RESULTS = [
    "called_strike",
    "swinging_strike",
    "swinging_strike_blocked",
    "foul_tip"
]


def create_second_data_table(pitch_data):

    # -------------------------------
    # Base summary
    # -------------------------------

    pitch_summary = (
        pitch_data.groupby("pitch_type")
        .agg(
            Pitch_Count=("pitch_type", "count"),
            Zone_Pitches=("zone", lambda x: ((x >= 1) & (x <= 9)).sum())
        )
    )

    total_pitches = len(pitch_data)
    total_two_strike = (pitch_data["strikes"] == 2).sum()

    pitch_summary["Usage"] = (pitch_summary["Pitch_Count"] / total_pitches * 100)

    pitch_summary["Zone%"] = (pitch_summary["Zone_Pitches"] / pitch_summary["Pitch_Count"] * 100)

    pitch_summary.drop(columns="Zone_Pitches", inplace=True)

    # -------------------------------
    # Calculate statistics
    # -------------------------------

    for pitch in pitch_summary.index:

        subset = pitch_data[pitch_data["pitch_type"] == pitch]

        balls_in_play = subset[subset["launch_speed"].notna()]

        first_pitches = subset[(subset["balls"] == 0) & (subset["strikes"] == 0)]

        two_strike = subset[subset["strikes"] == 2]

        # ---------------- HH% ----------------

        if len(balls_in_play):
            hh_pct = ((balls_in_play["launch_speed"] >= 95).mean() * 100)
        else:
            hh_pct = np.nan

        # ---------------- AB mask ----------------

        at_bat_events = [
            "single",
            "double",
            "triple",
            "home_run",
            "field_out",
            "force_out",
            "field_error",
            "grounded_into_double_play",
            "fielders_choice",
            "fielders_choice_out",
            "strikeout",
            "strikeout_double_play",
            "double_play",
            "triple_play",
            "other_out"
        ]

        at_bats = subset["events"].isin(at_bat_events)
        ab_count = int(at_bats.sum())

        # ---------------- xBA ----------------

        if ab_count:
            expected_hits = (subset.loc[at_bats, "estimated_ba_using_speedangle"].fillna(0).sum())
            xba = expected_hits / ab_count
        else:
            xba = np.nan

        # ---------------- SLG ----------------

        bases = (
            subset.loc[at_bats, "events"]
            .map({
                "single": 1,
                "double": 2,
                "triple": 3,
                "home_run": 4
            })
            .fillna(0)
        )

        if ab_count:
            slg = bases.sum() / ab_count
        else:
            slg = np.nan


        # ---------------- FPS% ----------------

        if len(first_pitches):
            fps_pct = (first_pitches["description"].isin(FIRST_PITCH_STRIKES).mean() * 100)
        else:
            fps_pct = np.nan

        # ---------------- CSW% ----------------

        csw_pct = (subset["description"].isin(CSW_RESULTS).mean() * 100)

        # ---------------- 2K Usage ----------------

        if total_two_strike:
            usage_2k = (len(two_strike) / total_two_strike * 100)
        else:
            usage_2k = np.nan

        # Store everything

        pitch_summary.loc[pitch, "HH%"] = hh_pct
        pitch_summary.loc[pitch, "xBA"] = xba
        pitch_summary.loc[pitch, "SLG"] = slg
        pitch_summary.loc[pitch, "FPS%"] = fps_pct
        pitch_summary.loc[pitch, "CSW%"] = csw_pct
        pitch_summary.loc[pitch, "2K %"] = usage_2k

    # -------------------------------
    # Count Usage
    # -------------------------------

    count_data = pitch_data.copy()

    count_data["Count"] = (count_data["balls"].astype(str)
        + "-"
        + count_data["strikes"].astype(str)
    )

    count_order = [
        "0-0", "0-1", "0-2",
        "1-0", "1-1", "1-2",
        "2-0", "2-1", "2-2",
        "3-0", "3-1", "3-2"
    ]

    count_usage = pd.pivot_table(
        count_data,
        index="pitch_type",
        columns="Count",
        values="release_speed",
        aggfunc="count",
        fill_value=0
    )

    count_usage = count_usage.reindex(columns=count_order, fill_value=0)
    column_totals = count_usage.sum(axis=0)
    column_totals = column_totals.replace(0, np.nan)

    count_usage = (count_usage.div(column_totals, axis=1) * 100)

    pitch_summary = pitch_summary.join(count_usage)

    # -------------------------------
    # Rounding
    # -------------------------------

    round_columns = [
        "Usage",
        "Zone%",
        "HH%",
        "CSW%",
        "FPS%",
        "2K %"
    ] + count_order

    pitch_summary[round_columns] = (pitch_summary[round_columns].round(1))

    pitch_summary["xBA"] = (pitch_summary["xBA"].round(3))

    pitch_summary["SLG"] = (pitch_summary["SLG"].round(3))

    # -------------------------------
    # Sort & Display
    # -------------------------------

    pitch_summary = pitch_summary.sort_values(
        "Usage",
        ascending=False
    )

    pitch_summary = pitch_summary[
        [
            "Usage",
            "Zone%",
            "HH%",
            "CSW%",
            "xBA",
            "SLG",
            "FPS%"
        ]
        + count_order
        + ["2K %"]
    ]

    display_table = pitch_summary.rename(
        index={
            pitch: info["name"]
            for pitch, info in PITCH_INFO.items()
        }
    )

    return pitch_summary, display_table
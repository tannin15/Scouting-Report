from pitch_dictionary import PITCH_INFO


def create_first_data_table(pitch_data, recent_data):

    # -----------------------------
    # MAIN PITCH BREAKDOWN TABLE
    # -----------------------------

    pitch_summary = pitch_data.groupby("pitch_type").agg(

        Pitch_Count=("pitch_type", "count"),
        Velo=("release_speed", "mean"),
        Max_Velo=("release_speed", "max"),
        RPM=("release_spin_rate", "mean"),
        Avg_IVB=("IVB_inches", "mean"),
        Avg_HB=("HB_inches", "mean"),
        Avg_Release_Height=("release_pos_z", "mean"),
        Zone_Pitches=("zone", lambda x: ((x >= 1) & (x <= 9)).sum())
    )


    # Usage

    pitch_summary["Usage"] = (
        pitch_summary["Pitch_Count"] / len(pitch_data) * 100
    )


    # Zone%

    pitch_summary["Zone%"] = (
        pitch_summary["Zone_Pitches"] / pitch_summary["Pitch_Count"] * 100
    )


    pitch_summary = pitch_summary.drop(columns="Zone_Pitches")


    # -----------------------------
    # LAST 30 DAY USAGE
    # -----------------------------

    if len(recent_data) > 0:

        recent_usage = (
            recent_data
            .groupby("pitch_type")
            .size()
            .div(len(recent_data))
            .mul(100)
            .rename("Usage_Last30")
        )

        pitch_summary = pitch_summary.join(recent_usage)

    else:
        pitch_summary["Usage_Last30"] = 0


    pitch_summary["Usage_Last30"] = (pitch_summary["Usage_Last30"].fillna(0))


    # -----------------------------
    # FORMAT TABLE LAYOUT
    # -----------------------------

    pitch_summary = (
        pitch_summary
        .sort_values(
            "Usage",
            ascending=False
        )
        .round({
            "Usage": 1,
            "Usage_Last30": 1,
            "Velo": 1,
            "Max_Velo": 1,
            "Avg_IVB": 1,
            "Avg_HB": 1,
            "Avg_Release_Height": 1,
            "Zone%": 1
        })
    )


    pitch_summary["RPM"] = (pitch_summary["RPM"].astype(int))


    # Top Table layout

    pitch_summary = pitch_summary[
        [
            "Pitch_Count",
            "Usage",
            "Usage_Last30",
            "Velo",
            "Max_Velo",
            "RPM",
            "Avg_IVB",
            "Avg_HB",
            "Avg_Release_Height",
            "Zone%"
        ]
    ]

    # Create a display version with full pitch names
    display_summary = pitch_summary.rename(
        index={pitch: info["name"] for pitch, info in PITCH_INFO.items()}
    )

    return pitch_summary, display_summary



from pathlib import Path

import matplotlib.pyplot as plt

from player_lookup import get_pitcher_data
from player_info import get_player_info
from header_stats import get_header_stats
from headshots import download_headshot
from table_one import create_first_data_table
from table_two import create_second_data_table
from heatmaps import pitch_heatmaps
from movement_plot import plot_pitch_movement
from arm_angle import plot_arm_angle
from extension import plot_release_point


# --------------------------------
# PROJECT PATHS
# --------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent


# --------------------------------
# GENERATE REPORT DATA
# --------------------------------

def generate_pitcher_report(search_name):
    """
    Generate all tables, graphics, player information, and split-specific
    content needed by the Streamlit app.

    Returns:
        {
            "shared": {...},
            "pages": {
                "Overall": {...},
                "vs RHH": {...},
                "vs LHH": {...},
            }
        }
    """

    # --------------------------------
    # PLAYER LOOKUP
    # --------------------------------

    pitcher_id, official_name, pitch_data, recent_data = get_pitcher_data(search_name)

    if pitch_data is None or pitch_data.empty:
        raise ValueError(
            f"No Statcast pitch data was found for {official_name}."
        )

    print(f"\nGenerating report for {official_name}...")

    # --------------------------------
    # PLAYER INFORMATION
    # --------------------------------

    player_info = get_player_info(pitcher_id, pitch_data)

    # --------------------------------
    # HEADSHOT
    # --------------------------------

    headshot_file = None

    if player_info.get("headshot_url"):
        headshot_path = SCRIPT_DIR / "temp_headshot.png"

        try:
            headshot_file = download_headshot(
                player_info["headshot_url"],
                save_path=str(headshot_path),
            )
        except Exception as error:
            # The report should still load if the headshot fails.
            print(f"Unable to download headshot: {error}")
            headshot_file = None

    # --------------------------------
    # SPLIT FULL-SEASON DATA
    # --------------------------------

    overall_data = pitch_data.copy()

    if "stand" not in pitch_data.columns:
        raise ValueError(
            "The pitch data does not contain the required 'stand' column."
        )

    rhh_data = pitch_data.loc[
        pitch_data["stand"].eq("R")
    ].copy()

    lhh_data = pitch_data.loc[
        pitch_data["stand"].eq("L")
    ].copy()

    # --------------------------------
    # SPLIT RECENT DATA
    # --------------------------------

    if recent_data is None:
        recent_data = pitch_data.iloc[0:0].copy()

    overall_recent = recent_data.copy()

    if "stand" in recent_data.columns:
        rhh_recent = recent_data.loc[
            recent_data["stand"].eq("R")
        ].copy()

        lhh_recent = recent_data.loc[
            recent_data["stand"].eq("L")
        ].copy()

    else:
        rhh_recent = recent_data.iloc[0:0].copy()
        lhh_recent = recent_data.iloc[0:0].copy()

    # --------------------------------
    # TABLE ONE
    # --------------------------------

    overall_table_one, overall_display_one = create_first_data_table(overall_data, overall_recent)

    rhh_table_one, rhh_display_one = create_first_data_table(rhh_data, rhh_recent)

    lhh_table_one, lhh_display_one = create_first_data_table(lhh_data, lhh_recent)

    # --------------------------------
    # TABLE TWO
    # --------------------------------

    overall_table_two, overall_display_two = create_second_data_table(overall_data)

    rhh_table_two, rhh_display_two = create_second_data_table(rhh_data)

    lhh_table_two, lhh_display_two = create_second_data_table(lhh_data)

    # --------------------------------
    # HEATMAPS
    # --------------------------------

    overall_heatmaps = pitch_heatmaps(overall_data, batter_side="ALL")

    rhh_heatmaps = pitch_heatmaps(rhh_data, batter_side="R")

    lhh_heatmaps = pitch_heatmaps(lhh_data, batter_side="L")

    # --------------------------------
    # MOVEMENT PLOTS
    # --------------------------------

    overall_movement = plot_pitch_movement(overall_data, official_name)

    rhh_movement = plot_pitch_movement(rhh_data, f"{official_name} vs RHH")

    lhh_movement = plot_pitch_movement(lhh_data, f"{official_name} vs LHH")

    # --------------------------------
    # SHARED VISUALIZATIONS
    # --------------------------------

    arm_angle = plot_arm_angle(overall_data)

    extension = plot_release_point(overall_data)

    # --------------------------------
    # HEADER STATISTICS
    # --------------------------------

    header = get_header_stats(pitcher_id)

    # --------------------------------
    # SHARED REPORT CONTENT
    # --------------------------------

    shared_report = {
        "pitcher_id": pitcher_id,
        "official_name": official_name,
        "player_info": player_info,
        "header": header,
        "headshot_file": headshot_file,
        "arm_angle": arm_angle,
        "extension": extension,
    }

    # --------------------------------
    # PAGE-SPECIFIC CONTENT
    # --------------------------------

    page_reports = {
        "Overall": {
            "split_label": "Overall",
            "pitch_data": overall_data,
            "recent_data": overall_recent,
            "table_one": overall_table_one,
            "display_table_one": overall_display_one,
            "table_two": overall_table_two,
            "display_table_two": overall_display_two,
            "heatmaps": overall_heatmaps,
            "movement_plot": overall_movement,
        },

        "vs RHH": {
            "split_label": "vs RHH",
            "pitch_data": rhh_data,
            "recent_data": rhh_recent,
            "table_one": rhh_table_one,
            "display_table_one": rhh_display_one,
            "table_two": rhh_table_two,
            "display_table_two": rhh_display_two,
            "heatmaps": rhh_heatmaps,
            "movement_plot": rhh_movement,
        },

        "vs LHH": {
            "split_label": "vs LHH",
            "pitch_data": lhh_data,
            "recent_data": lhh_recent,
            "table_one": lhh_table_one,
            "display_table_one": lhh_display_one,
            "table_two": lhh_table_two,
            "display_table_two": lhh_display_two,
            "heatmaps": lhh_heatmaps,
            "movement_plot": lhh_movement,
        },
    }

    return {
        "shared": shared_report,
        "pages": page_reports,
    }


# --------------------------------
# OPTIONAL COMMAND-LINE TEST
# --------------------------------

def main():
    search_name = input("Enter pitcher name: ").strip()

    if not search_name:
        print("No pitcher name was entered.")
        return

    try:
        report = generate_pitcher_report(search_name)

    except Exception as error:
        print(f"\nUnable to generate report: {error}")
        return

    shared = report["shared"]
    official_name = shared["official_name"]

    print(
        f"\nReport data successfully generated for "
        f"{official_name}."
    )

    print("\nPLAYER INFO")
    print(shared["player_info"])

    print("\nOVERALL TABLE ONE")
    print(report["pages"]["Overall"]["display_table_one"])

    print("\nOVERALL TABLE TWO")
    print(report["pages"]["Overall"]["display_table_two"])

    print("\nVS RHH TABLE ONE")
    print(report["pages"]["vs RHH"]["display_table_one"])

    print("\nVS RHH TABLE TWO")
    print(report["pages"]["vs RHH"]["display_table_two"])

    print("\nVS LHH TABLE ONE")
    print(report["pages"]["vs LHH"]["display_table_one"])

    print("\nVS LHH TABLE TWO")
    print(report["pages"]["vs LHH"]["display_table_two"])

    plt.show()


if __name__ == "__main__":
    main()
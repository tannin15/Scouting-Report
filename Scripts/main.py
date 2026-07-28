from player_lookup import get_pitcher_data
from player_info import get_player_info
from header_stats import get_header_stats
from table_one import create_first_data_table
from table_two import create_second_data_table
from heatmaps import pitch_heatmaps
from movement_plot import plot_pitch_movement
from arm_angle import plot_arm_angle
from extension import plot_release_point
import matplotlib.pyplot as plt


# --------------------------------
# PLAYER LOOKUP
# --------------------------------
search_name = input("Enter pitcher name: ")


pitcher_id, official_name, pitch_data, recent_data = get_pitcher_data(search_name)

player_info = get_player_info(pitcher_id, pitch_data)

from headshots import download_headshot

headshot_file = download_headshot(player_info["headshot_url"])

print(headshot_file)

# -------------------
# SPLIT OVERALL DATA
# -------------------

overall_data = pitch_data.copy()
rhh_data = pitch_data[pitch_data["stand"] == "R"].copy()
lhh_data = pitch_data[pitch_data["stand"] == "L"].copy()

# -------------------------
# SPLIT LAST 30 DAYS DATA
# -------------------------

overall_recent = recent_data.copy()
rhh_recent = recent_data[recent_data["stand"] == "R"].copy()
lhh_recent = recent_data[recent_data["stand"] == "L"].copy()


print(f"\nGenerating report for {official_name}...")


#-----------------------
# CREATE DATA TABLES
#-----------------------
overall_table_one, overall_display_one = create_first_data_table(overall_data, overall_recent)
rhh_table_one, rhh_display_one = create_first_data_table(rhh_data, rhh_recent)
lhh_table_one, lhh_display_one = create_first_data_table(lhh_data, lhh_recent)


overall_table_two, overall_display_two = create_second_data_table(overall_data)
rhh_table_two, rhh_display_two = create_second_data_table(rhh_data)
lhh_table_two, lhh_display_two = create_second_data_table(lhh_data)

#----------------------
# CREATE HEATMAPS
# ---------------------
overall_heatmaps = pitch_heatmaps(overall_data, batter_side= "All")
rhh_heatmaps = pitch_heatmaps(rhh_data, batter_side="R")
lhh_heatmaps = pitch_heatmaps(lhh_data, batter_side="L")


#--------------------------------
# CREATE VISUALIZATIONS
#--------------------------------
arm_angle = plot_arm_angle(overall_data)

extension = plot_release_point(overall_data)


#--------------------
# HEADER STATISTICS
#--------------------
header = get_header_stats(pitcher_id)


# print(overall_display_one)
# print()
# print(overall_display_two)
# print(heatmaps)
# print(header)
print(player_info)



# fig = plot_pitch_movement(pitch_data, official_name)
#plt.show()


import matplotlib.pyplot as plt
from PIL import Image


# Calibration constants
RUBBER_X = 0.002
GROUND_Y = 0.08

RHP_AVG_EXTENSION = 6.45
RHP_AVG_HEIGHT = 5.72

LHP_AVG_EXTENSION = 6.38
LHP_AVG_HEIGHT = 5.75

IMAGE_LEFT = RUBBER_X
IMAGE_RIGHT = 6.79
IMAGE_BOTTOM = GROUND_Y
IMAGE_TOP = 6.19

# Plot dimensions
X_MIN = 0
X_MAX = 7.75
Y_MIN = 0
Y_MAX = 6.9


def mirror_x(x_value):
    """
    Mirror an x-coordinate across the horizontal center
    of the extension graphic.
    """

    return X_MAX - x_value


def plot_release_point(pitch_data):

    if pitch_data is None or pitch_data.empty:
        return None

    pitcher_hand = str(pitch_data["p_throws"].iloc[0]).strip().upper()

    # Calculate the pitcher's average release point.
    avg_extension = pitch_data["release_extension"].mean()
    avg_height = pitch_data["release_pos_z"].mean()

    if pitcher_hand == "L":

        pitcher_img = Image.open("Images/rhp_extension.png")

        league_extension = LHP_AVG_EXTENSION
        league_height = LHP_AVG_HEIGHT

        # Mirror the silhouette across the graphic.
        image_extent = [
            mirror_x(IMAGE_LEFT),
            mirror_x(IMAGE_RIGHT),
            IMAGE_BOTTOM,
            IMAGE_TOP,
        ]

        # Mirror the plotted extension coordinates.
        plotted_extension = mirror_x(avg_extension)
        plotted_league_extension = mirror_x(league_extension)

    else:

        pitcher_img = Image.open("Images/rhp_extension.png")

        league_extension = RHP_AVG_EXTENSION
        league_height = RHP_AVG_HEIGHT

        # Keep the existing RHP layout unchanged.
        image_extent = [
            IMAGE_LEFT,
            IMAGE_RIGHT,
            IMAGE_BOTTOM,
            IMAGE_TOP,
        ]

        plotted_extension = avg_extension
        plotted_league_extension = league_extension

    # Create figure.
    fig, ax = plt.subplots(figsize=(5, 3))

    # Draw pitcher silhouette.
    ax.imshow(
        pitcher_img,
        extent=image_extent,
        aspect="equal",
        alpha=0.25,
        zorder=1,
    )

    # Plot pitcher release point.
    ax.scatter(
        plotted_extension,
        avg_height,
        s=100,
        color="red",
        edgecolor="black",
        linewidth=1,
        zorder=5,
        label="Pitcher",
    )

    # Plot handedness-specific MLB average.
    ax.scatter(
        plotted_league_extension,
        league_height,
        s=80,
        color="lightgray",
        edgecolor="black",
        linewidth=0.7,
        zorder=4,
        label="MLB Average",
    )

    # # Label the point
        # ax.text(
        #     avg_extension + 0.25,
        #     avg_height,
        #     f"{avg_extension:.2f} ft",
        #     fontsize=8,
        #     va="center",
        #     zorder = 10
        # )


    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)

    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    # Keep the title showing the real extension value,
    # not the mirrored plotting coordinate.
    ax.set_title(
        f"Extension: {avg_extension:.2f} ft"
    )

    plt.tight_layout()


    plt.close(fig)                          # removes the figure from pyplot's registry to free up some memory

    return fig

   
    

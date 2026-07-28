import numpy as np
import matplotlib.pyplot as plt

from scipy.ndimage import gaussian_filter
from matplotlib.patches import Rectangle, Polygon 
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import PowerNorm
from PIL import Image
from pitch_dictionary import PITCH_INFO



lhb_img = Image.open("Images/lefty_batter.png")
rhb_img = Image.open("Images/righty_batter.png")

# Create specific color mapping 
# Red = Highest Density; Blue = Lowest Density; White = background

heatmap_cmap = LinearSegmentedColormap.from_list(
    "PitchHeat",
    [
        "#FAFDFF",
        "#DCEEFF",
        "#7DB8FF",
        "#1C64F2",
        "#00D4FF",
        "#FFE34A",
        "#FF5A36",
        "#D60000"
    ],
    N=512
)

heatmap_cmap.set_bad("white")           # makes NaN pitches white

#-------------------------------------------------------------------------------------------
# ZONE AND BATTER LOCATION SETTINGS
#-------------------------------------------------------------------------------------------

# STRIKE ZONE DIMENSIONS (Generalized)
ZONE_LEFT = -0.83
ZONE_RIGHT = 0.83

ZONE_BOTTOM = 1.55
ZONE_TOP = 3.30

ZONE_WIDTH = ZONE_RIGHT - ZONE_LEFT
ZONE_HEIGHT = ZONE_TOP - ZONE_BOTTOM

# SHADOW ZONE DIMENSIONS
SHADOW_X = 0.23
SHADOW_Y = 0.19


# Batter image dimensions (in plot coordinates)
BATTER_WIDTH = 1.25
BATTER_HEIGHT = 5.9

# Batter distane from edge of plate
BATTER_GAP = 0.6

# Position of the bottom-left corner of the image
BATTER_X = ZONE_RIGHT + BATTER_GAP
BATTER_Y = 0                        # Raise/lower the entire batter here

# EXTENT FOR BATTER IMAGE.OPEN
RHB_EXTENT = [
    ZONE_RIGHT + BATTER_GAP,
    ZONE_RIGHT + BATTER_GAP + BATTER_WIDTH,
    BATTER_Y,
    BATTER_Y + BATTER_HEIGHT
]

LHB_EXTENT = [
    ZONE_LEFT - BATTER_GAP - BATTER_WIDTH,
    ZONE_LEFT - BATTER_GAP,
    BATTER_Y,
    BATTER_Y + BATTER_HEIGHT
]
# -----------------
# HELPER FUNCTIONS
# -----------------

def draw_strike_zone(ax):

    zone = Rectangle(
        (ZONE_LEFT, ZONE_BOTTOM),
        ZONE_WIDTH,
        ZONE_HEIGHT,
        fill=False,
        linewidth=1.5,
        color="#222222"
    )

    shadow = Rectangle(
        (
            ZONE_LEFT - SHADOW_X,
            ZONE_BOTTOM - SHADOW_Y
        ),
        ZONE_WIDTH + 2*SHADOW_X,
        ZONE_HEIGHT + 2*SHADOW_Y,
        fill=False,
        linestyle=":",
        linewidth=1,
        edgecolor="gray",
        zorder=14
    )

    ax.add_patch(zone)
    ax.add_patch(shadow)


def draw_home_plate(ax):

    home_plate = Polygon(
        [
            (ZONE_LEFT,0),
            (ZONE_RIGHT,0),
            (ZONE_RIGHT,.12),
            (0,.36),
            (ZONE_LEFT,.12)
        ],
        closed=True,
        facecolor="white",
        edgecolor="black",
        linewidth=1.5
    )

    ax.add_patch(home_plate)


def draw_batter(ax,batter_side):

    if batter_side=="R":

        ax.imshow(                                              # Because plots are mirrored to appear from pitcher POV,
            lhb_img,                                            # batter images need to be flipped (R = LHBimg) to display 
            extent=LHB_EXTENT,                                  # from the proper side
            aspect="auto",                                      
            alpha=.2,
            zorder=1
        )

    elif batter_side=="L":

        ax.imshow(
            rhb_img,
            extent=RHB_EXTENT,
            aspect="auto",
            alpha=.2,
            zorder=1
        )

    else:

        ax.imshow(
            rhb_img,
            extent=RHB_EXTENT,
            aspect="auto",
            alpha=.2,
            zorder=1
        )

        ax.imshow(
            lhb_img,
            extent=LHB_EXTENT,
            aspect="auto",
            alpha=.2,
            zorder=1
        )

# ---------------------------------------
# DRAW ONE HEATMAP PER PITCH TYPE
# ---------------------------------------

def create_heatmap(pitch_subset, pitch_name, usage_pct, batter_side):

    fig, ax = plt.subplots(
        figsize=(3.4,4)
    )

    location_data = pitch_subset.dropna(subset=["plate_x", "plate_z"]).copy()

    x = location_data["plate_x"]
    z = location_data["plate_z"]

    if len(location_data) < 15:
        plt.close(fig)
        return None

    hist, xedges, yedges = np.histogram2d(
        x,
        z,
        bins=(80,80),
        range=[[-2,2],[0,5]]
    )

    density = gaussian_filter(
        hist,
        sigma=2.5
    )

    if density.max()==0:
        plt.close(fig)
        return None

    density /= density.max()

    plot_density = density.copy()

    plot_density = (plot_density-.08)/(1-.08)

    plot_density = np.clip(
        plot_density,
        0,
        1
    )

    plot_density = plot_density**1.2

    plot_density[plot_density<.02] = np.nan

    ax.imshow(
        plot_density.T,
        origin="lower",
        extent=[
            xedges[0],
            xedges[-1],
            yedges[0],
            yedges[-1]
        ],
        cmap=heatmap_cmap,
        norm=PowerNorm(gamma=.7),
        interpolation="bilinear",
        aspect="equal"
    )

    draw_strike_zone(ax)
    draw_home_plate(ax)
    draw_batter(ax,batter_side)

    ax.set_xlim(2.65,-2.65)
    ax.set_ylim(-.6,5.3)

    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(
        f"{pitch_name}\n{usage_pct:.1f}%",
        fontsize=6,
        fontweight="bold"
    )

    plt.close(fig)                          # removes the figure from pyplot's registry to free up some memory

    return fig


# ------------------------------
# PRODUCE HEATMAPS
# ------------------------------

def pitch_heatmaps(pitch_data, batter_side):

    heatmaps = {}

    unique_pitches = (pitch_data["pitch_type"].value_counts().index)

    for pitch in unique_pitches:

        pitch_subset = pitch_data[pitch_data["pitch_type"]==pitch]

        pitch_name = PITCH_INFO[pitch]["name"]

        usage_pct = (len(pitch_subset)/len(pitch_data)*100)

        fig = create_heatmap(pitch_subset, pitch_name, usage_pct, batter_side)

        if fig is not None:
            heatmaps[pitch] = fig

    return heatmaps


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
from pathlib import Path


RHP_LOW = Image.open(IMAGE_DIR / "rhp_low.png")
RHP_MID = Image.open(IMAGE_DIR / "rhp_mid.png")
RHP_HIGH = Image.open(IMAGE_DIR / "rhp_high.png")

LHP_LOW = Image.open(IMAGE_DIR / "lhp_low.png")
LHP_MID = Image.open(IMAGE_DIR / "lhp_mid.png")
LHP_HIGH = Image.open(IMAGE_DIR / "lhp_high.png")

#----------------------------------------------------------
# Dictionary for proper RHP/LHP arm plot placement on pngs
#----------------------------------------------------------

ARM_CONFIG = {

    ("R", "LOW"): {
        "image": RHP_LOW,
        "shoulder": (0.145, 1.195),
        "arm_length": 0.75,
        "xlim": (-0.8, 1.01),
        "ylim": (0, 1.75),
        "shoulder_width": 0.068,
        "hand_width": 0.027,
        "hand_size": 60,
        "angle_offset": 0,
    },

    ("R", "MID"): {
        "image": RHP_MID,
        "shoulder": (0.15, 1.37),
        "arm_length": 0.7,
        "xlim": (-0.7, 1.01),
        "ylim": (0, 1.85),
        "shoulder_width": 0.068,
        "hand_width": 0.027,
        "hand_size": 65,
        "angle_offset": 0,
    },

    ("R", "HIGH"): {
        "image": RHP_HIGH,
        "shoulder": (0.415, 1.54),
        "arm_length": 0.6,
        "xlim": (-0.3, 1.01),
        "ylim": (0, 2.15),
        "shoulder_width": 0.059,
        "hand_width": 0.021,
        "hand_size": 60,
        "angle_offset": 0,
    },

    ("L", "LOW"): {
        "image": LHP_LOW,
        "shoulder": (0.845, 1.195),
        "arm_length": 0.7,
        "xlim": (-0.01, 1.6),
        "ylim": (0, 1.75),
        "shoulder_width": 0.068,
        "hand_width": 0.027,
        "hand_size": 60,
        "angle_offset": 0,
    },

    ("L", "MID"): {
        "image": LHP_MID,
        "shoulder": (0.855, 1.37),
        "arm_length": 0.63,
        "xlim": (-0.01, 1.6),
        "ylim": (0, 1.83),
        "shoulder_width": 0.068,
        "hand_width": 0.03,
        "hand_size": 60,
        "angle_offset": 0,
    },

    ("L", "HIGH"): {
        "image": LHP_HIGH,
        "shoulder": (0.59, 1.54),
        "arm_length": 0.56,
        "xlim": (-0.05, 1.1),
        "ylim": (0, 2.15),
        "shoulder_width": 0.058,
        "hand_width": 0.022,
        "hand_size": 65,
        "angle_offset": 0,
    }

}

def get_arm_profile(arm_angle, throws):
    if arm_angle <= 6:
        slot = "LOW"

    elif arm_angle > 6 and arm_angle < 39:
        slot = "MID"

    else:
        slot = "HIGH"

    return ARM_CONFIG[(throws, slot)]

#---------------------------------------
# DRAW ARM POLYGON SHAPE
#---------------------------------------
def draw_arm_polygon(ax, shoulder_x, shoulder_y, hand_x, hand_y, shoulder_width, hand_width):

    dx = hand_x - shoulder_x
    dy = hand_y - shoulder_y

    length = np.hypot(dx, dy)

    px = -dy / length
    py = dx / length

    points = [
        (   shoulder_x + px*shoulder_width/2,
        shoulder_y + py*shoulder_width/2),

        (   shoulder_x - px*shoulder_width/2,
        shoulder_y - py*shoulder_width/2),

        (   hand_x - px*hand_width/2,
        hand_y - py*hand_width/2),

        (   hand_x + px*hand_width/2,
        hand_y + py*hand_width/2),
    ]

    arm = Polygon(
        points,
        closed=True,
        facecolor="black",
        edgecolor="black",
        zorder=5
    )

    ax.add_patch(arm)
    



def plot_arm_angle(pitch_data):
    
    # Average arm angle for pitcher
    arm_angle = pitch_data["arm_angle"].dropna().mean()
    
    throws = pitch_data["p_throws"].iloc[0]

    # Assign the proper png
    config = get_arm_profile(arm_angle, throws)

    # Create figure
    fig, ax = plt.subplots(figsize=(2,4))

    ax.imshow(
        config["image"],
        extent=[0,1,0,1.7],           # how big is the image in relation to the graph
        aspect="equal",
        zorder=0
    )

    shoulder_x, shoulder_y = config["shoulder"]
    

    if throws == "R":
        # 0° points to the LEFT
        theta = np.deg2rad(180 - arm_angle)

    else:
        # 0° points to the RIGHT
        theta = np.deg2rad(arm_angle)

    hand_x = shoulder_x + config["arm_length"] * np.cos(theta)
    hand_y = shoulder_y + config["arm_length"] * np.sin(theta)


    draw_arm_polygon(ax, 
                shoulder_x, 
                shoulder_y, 
                hand_x, 
                hand_y, 
                config["shoulder_width"], 
                config["hand_width"])

    # Plot hand location
    ax.scatter(hand_x, 
            hand_y, 
            s=config["hand_size"],
            facecolor="white",
            edgecolor="forestgreen",
            linewidth=1,
            zorder=6
        )
    
    # Plot shoulder point to round off the polygon
    ax.scatter(
        shoulder_x,
        shoulder_y,
        s=100,                              # adjust until it matches arm width
        color="black",
        zorder=5
    )

    release_height = pitch_data["release_pos_z"].mean()

    ax.text(
        0.5,
        1.05,
        f"Release Height: {release_height:.1f} ft",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=8,
        fontweight="bold"
    )

    ax.set_xlim(*config["xlim"])
    ax.set_ylim(*config["ylim"])    

    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)


    plt.close(fig)                          # removes the figure from pyplot's registry to free up some memory

    return fig



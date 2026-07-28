from matplotlib.patches import Ellipse
from scipy.stats import chi2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from pitch_dictionary import PITCH_INFO


MOVEMENT_CLOUD_CONFIDENCE = 0.45
MOVEMENT_CLOUD_SCALE = 0.75

#-------------------------------------------------------------------
# Confidence is how much of the data the ellipse/circle represents
# Scale is the overall size of the ellipse/circle
#-------------------------------------------------------------------

def draw_pitch_cloud(x, y, ax, color, confidence=MOVEMENT_CLOUD_CONFIDENCE):


    """
    Draw a confidence ellipse around the movement cloud.

    confidence:
        0.40 = tight core
        0.50 = recommended
        0.68 = standard
        0.80 = larger
    """

    x = np.asarray(x)
    y = np.asarray(y)

    if len(x) < 5:
        return

    # Mean location
    mean_x = np.mean(x)
    mean_y = np.mean(y)

    # Covariance matrix
    cov = np.cov(x, y)

    # Eigenvalues/eigenvectors
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Sort largest -> smallest
    order = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    # Rotation angle
    angle = np.degrees(
            np.arctan2(
                eigenvectors[1, 0],
                eigenvectors[0, 0]
            )
        )

    # Scale factor for desired confidence
    scale = np.sqrt(chi2.ppf(confidence, df=2))

    width = 2 * scale * np.sqrt(eigenvalues[0])
    height = 2 * scale * np.sqrt(eigenvalues[1])

    # Apply visual scaling
    width *= MOVEMENT_CLOUD_SCALE
    height *= MOVEMENT_CLOUD_SCALE

    ellipse = Ellipse(
    (mean_x, mean_y),
    width,
    height,
    angle=angle,
    facecolor="none",
    edgecolor=color,
    linewidth=2,
    linestyle="--",
    zorder=5
    )

    ellipse.set_path_effects(
        [pe.Stroke(
            linewidth=3, 
            foreground="black"),
            pe.Normal()]
            )

    ax.add_patch(ellipse)
    


def plot_pitch_movement(pitch_data, official_name):

    fig, ax = plt.subplots(figsize=(9, 9))

    # Plot each pitch type
    for pitch in sorted(pitch_data["pitch_type"].unique()):

        if pitch not in PITCH_INFO:
            continue

        subset = pitch_data[pitch_data["pitch_type"] == pitch]

        color = PITCH_INFO[pitch]["color"]

        x = subset["HB_inches"]
        y = subset["IVB_inches"]

        # Scatter cloud
        ax.scatter(
            x,
            y,
            s=18,
            alpha=.35,
            color=color,
            edgecolors="none"
        )

        # Ellipse
        draw_pitch_cloud(
        x,
        y,
        ax,
        color,
        confidence=0.50
        )
        
        # Average location
        avg_x = x.mean()
        avg_y = y.mean()

        # Label
        ax.text(
            avg_x + 2.5,
            avg_y + 1,
            PITCH_INFO[pitch]["name"],
            fontsize=12,
            fontweight="bold",
            color=color
        )

    # Center lines
    ax.axhline(0, color="black", linewidth=2)
    ax.axvline(0, color="black", linewidth=2)

    ax.set_xlim(-25, 25)
    ax.set_ylim(-25, 25)

    # Major ticks every 5 inches
    ticks = np.arange(-25, 26, 5)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)

    ax.set_aspect("equal")

    ax.grid(True, linestyle="--", alpha=.35)

    ax.set_xlabel(
        "Horizontal Break (in)",
        fontsize=6,
        fontweight="bold"
    )

    ax.set_ylabel(
        "Induced Vertical Break (in)",
        fontsize=6,
        fontweight="bold"
    )

    ax.tick_params(labelsize=8)

    
    plt.tight_layout()


    plt.close(fig)                          # removes the figure from pyplot's registry to free up some memory


    return fig
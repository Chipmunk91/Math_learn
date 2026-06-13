"""Generate the social-share (Open Graph / Twitter) card for the landing page.

Produces a 1200x630 PNG at assets/og-card.png — the preview image that
Reddit, Twitter, Slack, etc. show when someone shares the site URL. Run
once and commit the PNG; the WASM build copies assets/ to site/assets/.

    python scripts/make_og_card.py
"""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "assets" / "og-card.png"

INK = "#1d2733"
GREY = "#56636f"
BLUE = "#5b7db1"

# 1200x630 at 100 dpi.
fig = plt.figure(figsize=(12, 6.3), dpi=100)
fig.patch.set_facecolor("white")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 12)
ax.set_ylim(0, 6.3)
ax.axis("off")

# --- faint flow-field backdrop: a damped spiral, streamplot in pale blue ---
gx, gy = np.meshgrid(np.linspace(0, 12, 60), np.linspace(0, 6.3, 32))
cx, cy = 8.7, 3.15           # swirl centre, over on the right
u = (gy - cy) - 0.12 * (gx - cx)
v = -(gx - cx) - 0.12 * (gy - cy)
ax.streamplot(
    gx, gy, u, v,
    color=BLUE, density=1.5, linewidth=0.8, arrowsize=0.7,
    arrowstyle="-|>",
)

# soft white veil on the left so the text sits on near-white
veil = plt.Rectangle((0, 0), 7.6, 6.3, color="white", alpha=0.78, zorder=2)
ax.add_patch(veil)

# --- text block ------------------------------------------------------------
ax.text(0.7, 4.5, "Differential Equations",
        fontsize=58, fontweight="bold", color=INK, zorder=3,
        family="DejaVu Sans")
ax.text(0.72, 3.55, "an interactive, visual playground",
        fontsize=30, color=BLUE, zorder=3, family="DejaVu Sans")
ax.text(0.72, 2.55,
        "Slope fields to chaos — drag the sliders,\nplay the animations, run the code.",
        fontsize=23, color=GREY, zorder=3, family="DejaVu Sans",
        linespacing=1.4)
ax.text(0.72, 0.8, "runs entirely in your browser  ·  no prerequisites  ·  free & open",
        fontsize=17, color=GREY, zorder=3, family="DejaVu Sans")

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, facecolor="white")
print(f"wrote {OUT}  ({OUT.stat().st_size // 1024} KB)")

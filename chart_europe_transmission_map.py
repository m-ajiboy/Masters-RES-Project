"""Builds a schematic map of Germany's real cross-border transmission links to its 10 real
neighbours (Phase 43), positioned using each country's real capital-city coordinates so the
layout is geographically sensible, with line thickness and colour representing the real
flow-derived transmission capacity (MW) computed in Phase 43. Not a real basemap/shapefile -
a deliberate, simple schematic (no extra heavy geo dependencies needed), honestly labelled
as such."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
with open(rf"{ROOT}\examples\backtest\RestOfEurope2023\allzones_computed_numbers.json") as f:
    DATA = json.load(f)

# France was built separately in Phase 42 (its own dedicated pilot, before the 9-country
# AllZones generator existed), so it is not in allzones_computed_numbers.json - added here
# from Phase 42's own real computed output (build_france_zone_data.py): DE->FR 3,014.9 MW,
# FR->DE 3,678.6 MW, both real 98th-percentile-of-2023-flow figures, same methodology as
# every other country.
DATA["FR"] = {"de_to": 3014.9, "to_de": 3678.6}

# Real capital-city coordinates (lat, lon) - standard, well-established geographic facts.
COORDS = {
    "DE": (52.52, 13.405),   # Berlin
    "AT": (48.21, 16.37),    # Vienna
    "BE": (50.85, 4.35),     # Brussels
    "CZ": (50.08, 14.44),    # Prague
    "DK": (55.68, 12.57),    # Copenhagen
    "NO": (59.91, 10.75),    # Oslo
    "NL": (52.37, 4.90),     # Amsterdam
    "PL": (52.23, 21.01),    # Warsaw
    "SE": (59.33, 18.07),    # Stockholm
    "CH": (46.95, 7.45),     # Bern
    "FR": (48.86, 2.35),     # Paris
}
FULL_NAMES = {"DE": "Germany", "AT": "Austria", "BE": "Belgium", "CZ": "Czech Republic",
              "DK": "Denmark", "NO": "Norway", "NL": "Netherlands", "PL": "Poland",
              "SE": "Sweden", "CH": "Switzerland", "FR": "France"}

fig, ax = plt.subplots(figsize=(11, 10))

de_lat, de_lon = COORDS["DE"]

# Draw links (line width scaled to real DE<->country capacity, direction-averaged for one line)
caps = {code: (d["de_to"] + d["to_de"]) / 2 for code, d in DATA.items()}
max_cap = max(caps.values())
min_cap = min(caps.values())

for code, d in DATA.items():
    lat, lon = COORDS[code]
    cap = caps[code]
    lw = 1.5 + 10 * (cap - min_cap) / (max_cap - min_cap)
    color = plt.cm.YlOrRd(0.3 + 0.7 * (cap - min_cap) / (max_cap - min_cap))
    ax.plot([de_lon, lon], [de_lat, lat], linewidth=lw, color=color,
             solid_capstyle="round", zorder=2, alpha=0.85)

# Draw country nodes with ONE combined label each (name + capacity together), offset
# radially outward from Germany. A single label per country - rather than a separate
# mid-line capacity label plus a separate name label - avoids the two-label collisions
# that kept recurring in the crowded Benelux cluster (confirmed directly across three
# earlier layout attempts).
for code, (lat, lon) in COORDS.items():
    is_de = code == "DE"
    ax.scatter([lon], [lat], s=650 if is_de else 320,
               color="#1f3a4d" if is_de else "#ffffff",
               edgecolors="#1f3a4d", linewidths=2.2, zorder=5)
    if is_de:
        ax.text(lon, lat + 1.3, "Germany", fontsize=13, ha="center", va="bottom",
                weight="bold", color="#1f3a4d", zorder=6,
                path_effects=[pe.withStroke(linewidth=3, foreground="white")])
    else:
        dx, dy = lon - de_lon, lat - de_lat
        norm = (dx ** 2 + dy ** 2) ** 0.5
        off_lon = lon + 1.0 * dx / norm
        off_lat = lat + 1.0 * dy / norm
        label = f"{FULL_NAMES[code]}\n{caps[code]:,.0f} MW"
        ax.text(off_lon, off_lat, label, fontsize=10.5, ha="center", va="center",
                color="#1f3a4d", zorder=6, linespacing=1.4,
                path_effects=[pe.withStroke(linewidth=3.5, foreground="white")])

ax.set_title("Germany's Real Cross-Border Transmission Capacity to All 10 Real Neighbours",
             fontsize=15, weight="bold", pad=14)
ax.text(0.5, -0.06,
        "Schematic layout using real capital-city positions (not a geographic basemap) - line width and colour show real,\n"
        "flow-derived transmission capacity (Phase 43). Sweden uses the real Baltic Cable nameplate capacity (Phase 35's\n"
        "SE_4 flow data was never obtained).",
        transform=ax.transAxes, ha="center", va="top", fontsize=9.5, color="#5a605c", style="italic")

ax.set_xlim(-9, 27)
ax.set_ylim(41, 65)
ax.set_aspect(1.6)
ax.axis("off")

plt.tight_layout()
out_path = rf"{ROOT}\chart_europe_transmission_map.png"
plt.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
print(f"Saved {out_path}")

"""Plots the raw V2 (component-split) demand profile - load (MW) against time.

Produces two charts from the same underlying data:
  1. The full 2027 calendar year (load_profile_v2_raw.png)
  2. A one-week zoom (load_profile_v2_oneweek.png), so the daily up/down cycle and the
     weekday-vs-weekend pattern are actually visible instead of compressed into a blur.

Kept simple and commented step-by-step - written to also work as a quick pandas/matplotlib
refresher, not just a one-off script.
"""
import matplotlib
matplotlib.use("Agg")  # renders to a file instead of trying to open an interactive window
import matplotlib.pyplot as plt
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
PATH = rf"{ROOT}\examples\backtest\Germany2027_DemandV2\timeseries\load_v2_split.csv"

# ---- 1. Load the data ----
# AMIRIS timeseries files have no header row and are semicolon-delimited:
#   2027-01-01_00:00:00;74123.4567
# so we tell pandas the column names ourselves and give it the delimiter explicitly.
df = pd.read_csv(PATH, sep=";", header=None, names=["ts", "mw"])

# The timestamp column arrives as plain text. Converting it to a real pandas datetime
# type is what lets matplotlib draw a proper time axis (with date ticks, correct
# spacing between points, etc.) instead of treating the timestamps as arbitrary strings.
df["ts"] = pd.to_datetime(df["ts"], format="%Y-%m-%d_%H:%M:%S")

print(f"Loaded {len(df)} rows: {df['ts'].min()} to {df['ts'].max()}")
print(f"min: {df['mw'].min():.0f} MW, max: {df['mw'].max():.0f} MW, mean: {df['mw'].mean():.0f} MW")


# ---- 2. Small helper so both charts share the same look ----
def make_plot(data, title, out_name, linewidth=0.6):
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(data["ts"], data["mw"], color="#1F3A4D", linewidth=linewidth)
    ax.set_xlabel("Time")
    ax.set_ylabel("Load (MW)")
    ax.set_title(title)
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()  # angles the date labels so they don't overlap each other
    plt.tight_layout()
    plt.savefig(rf"{ROOT}\{out_name}", dpi=150)
    plt.close(fig)  # free the figure from memory - matters if you ever loop over many plots
    print(f"Saved {out_name}")


# ---- 3. Full year ----
make_plot(df, "Germany 2027 Demand Profile - V2 (component-split build), full year",
          "load_profile_v2_raw.png")

# ---- 4. One-week zoom ----
# Boolean masking: this builds a True/False Series (one value per row) that's True only
# where the timestamp falls inside our chosen week, then df[mask] keeps just those rows.
week_start = pd.Timestamp("2027-01-11")  # a Monday
week_end = pd.Timestamp("2027-01-18")    # the following Monday (7 full days)
mask = (df["ts"] >= week_start) & (df["ts"] < week_end)
week_df = df[mask]

make_plot(week_df, "Germany 2027 Demand Profile - V2, one-week zoom (11-17 Jan 2027)",
          "load_profile_v2_oneweek.png", linewidth=1.6)

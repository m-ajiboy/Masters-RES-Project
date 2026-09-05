"""Breaks the AMIRIS-vs-Brainpool correlation down by month, hour-of-day, and weekday/weekend
for Germany2028 and Germany2029 (both at their current default 30,000 MW import ceiling) -
the same diagnostic method as Phase 10/23 for 2027, but never yet run on the out-of-sample
years. Goal: find out WHERE these years' gaps concentrate, and whether that sheds light on
why the import ceiling's ideal value reverses out-of-sample (Phase 25-27)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"


def load_amiris(path):
    dam = pd.read_csv(path, sep=";")
    dam["ts"] = pd.to_datetime(dam["TimeStep"])
    return dam.set_index("ts")["ElectricityPriceInEURperMWH"]


def run(year, result_folder):
    bp_full = load_brainpool_price(year)
    bp = bp_full[bp_full.index < f"{year}-12-31"] if year == 2028 else bp_full

    amiris = load_amiris(rf"{ROOT}\examples\backtest\Germany{year}\{result_folder}\DayAheadMarketSingleZone.csv")

    joined = pd.DataFrame({"bp": bp, "amiris": amiris}).dropna()
    joined["month"] = joined.index.month
    joined["hour"] = joined.index.hour
    joined["weekday"] = joined.index.dayofweek < 5

    shortage_mask = joined["amiris"] >= 2999.9
    clean = joined[~shortage_mask]
    print(f"\n=== Germany{year} (30,000 MW default): {len(joined)} hours, "
          f"{shortage_mask.sum()} shortage hours excluded ===")
    print(f"Overall (excl-shortage) r={clean['bp'].corr(clean['amiris']):.4f}, "
          f"bias={(clean['amiris']-clean['bp']).mean():+.2f}, "
          f"mae={(clean['amiris']-clean['bp']).abs().mean():.2f}")

    month_stats = clean.groupby("month").apply(
        lambda g: pd.Series({"r": g["bp"].corr(g["amiris"]), "bias": (g["amiris"] - g["bp"]).mean(),
                              "mae": (g["amiris"] - g["bp"]).abs().mean()}), include_groups=False)
    print("\n--- By month ---")
    print(month_stats.round(2).to_string())

    hour_stats = clean.groupby("hour").apply(
        lambda g: pd.Series({"r": g["bp"].corr(g["amiris"]), "bias": (g["amiris"] - g["bp"]).mean(),
                              "mae": (g["amiris"] - g["bp"]).abs().mean()}), include_groups=False)
    print("\n--- By hour of day ---")
    print(hour_stats.round(2).to_string())

    print("\n--- Weekday vs weekend ---")
    for is_weekday, label in [(True, "Weekday"), (False, "Weekend")]:
        g = clean[clean["weekday"] == is_weekday]
        print(f"{label}: n={len(g)}  r={g['bp'].corr(g['amiris']):.3f}  "
              f"bias={(g['amiris']-g['bp']).mean():+.2f}  mae={(g['amiris']-g['bp']).abs().mean():.2f}")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes[0, 0].bar(month_stats.index, month_stats["r"], color="#0072B2")
    axes[0, 0].set_title("Correlation (r) by month")
    axes[0, 0].axhline(clean["bp"].corr(clean["amiris"]), color="#D55E00", linestyle="--", label="full-year avg")
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].bar(month_stats.index, month_stats["bias"], color="#009E73")
    axes[0, 1].set_title("Bias (AMIRIS - Brainpool) by month")
    axes[0, 1].axhline(0, color="black", linewidth=0.8)
    axes[0, 1].grid(alpha=0.3)

    axes[1, 0].bar(hour_stats.index, hour_stats["r"], color="#0072B2")
    axes[1, 0].set_title("Correlation (r) by hour of day")
    axes[1, 0].axhline(clean["bp"].corr(clean["amiris"]), color="#D55E00", linestyle="--", label="full-year avg")
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].bar(hour_stats.index, hour_stats["bias"], color="#009E73")
    axes[1, 1].set_title("Bias (AMIRIS - Brainpool) by hour of day")
    axes[1, 1].axhline(0, color="black", linewidth=0.8)
    axes[1, 1].grid(alpha=0.3)

    fig.suptitle(f"Where does AMIRIS-vs-Brainpool tracking break down for Germany{year}?\n"
                 f"(30,000 MW default, shortage hours excluded)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out = rf"{ROOT}\correlation_breakdown_{year}.png"
    plt.savefig(out, dpi=150)
    print(f"\nSaved {out}")


run(2028, "result_Germany2028")
run(2029, "result_Germany2029")

"""
Compare AMIRIS-simulated day-ahead price against real historical price.

Usage:
    python compare_price.py --sim result_Germany2018/DayAheadMarketSingleZone.csv \
                             --real historical_price_2018.csv --year 2018
"""
import argparse
import pandas as pd


def load_simulated(path: str) -> pd.Series:
    df = pd.read_csv(path, sep=";")
    df["TimeStep"] = pd.to_datetime(df["TimeStep"])
    df = df.set_index("TimeStep")
    return df["ElectricityPriceInEURperMWH"].rename("simulated")


def load_real(path: str, timestamp_col: str, price_col: str) -> pd.Series:
    """Adjust timestamp_col / price_col to match whatever your downloaded
    SMARD/ENTSO-E export actually calls its columns."""
    df = pd.read_csv(path)
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    df = df.set_index(timestamp_col)
    series = df[price_col].rename("real")
    return series[~series.index.duplicated(keep="first")]


def compare(sim: pd.Series, real: pd.Series) -> pd.DataFrame:
    joined = pd.concat([sim, real], axis=1).dropna()
    joined["error"] = joined["simulated"] - joined["real"]
    return joined


def report(label: str, joined: pd.DataFrame):
    mae = joined["error"].abs().mean()
    rmse = (joined["error"] ** 2).mean() ** 0.5
    corr = joined["simulated"].corr(joined["real"])
    print(f"\n{label}")
    print(f"  Hours compared: {len(joined)}")
    print(f"  MAE:  {mae:.2f} EUR/MWh")
    print(f"  RMSE: {rmse:.2f} EUR/MWh")
    print(f"  Correlation: {corr:.3f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim", required=True)
    parser.add_argument("--real", required=True)
    parser.add_argument("--real-time-col", default="Timestamp")
    parser.add_argument("--real-price-col", default="price_eur_mwh")
    parser.add_argument(
        "--split-date",
        default=None,
        help="Optional date (YYYY-MM-DD) to additionally report metrics "
        "separately before/after, e.g. a market-zone-split date",
    )
    args = parser.parse_args()

    sim = load_simulated(args.sim)
    real = load_real(args.real, args.real_time_col, args.real_price_col)
    joined = compare(sim, real)

    report("Full period", joined)

    if args.split_date:
        split = pd.Timestamp(args.split_date)
        report(f"Before {args.split_date}", joined[joined.index < split])
        report(f"On/after {args.split_date}", joined[joined.index >= split])

    joined.to_csv("price_comparison.csv", sep=";")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(14, 5))
        joined["simulated"].plot(ax=ax, alpha=0.8, label="AMIRIS simulated")
        joined["real"].plot(ax=ax, alpha=0.8, label="Real (SMARD)")
        if args.split_date:
            ax.axvline(pd.Timestamp(args.split_date), color="black", linestyle="--", linewidth=1,
                       label=f"Zone split ({args.split_date})")
        ax.set_ylabel("EUR/MWh")
        ax.set_title("AMIRIS simulated vs. real day-ahead price — Germany 2018")
        ax.legend()
        plt.tight_layout()
        plt.savefig("price_comparison.png")
        print("\nSaved plot to price_comparison.png")
    except ImportError:
        print("\nmatplotlib not installed — skipping plot (pip install matplotlib)")


if __name__ == "__main__":
    main()

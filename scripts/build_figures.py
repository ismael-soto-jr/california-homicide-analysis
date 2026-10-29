"""Produce portfolio figures and aggregate CSVs from verified homicide source records.

Default: python scripts/build_figures.py
Without restricted raw data: python scripts/build_figures.py --from-summaries

Counts describe source victim records, not unique incidents or per-capita rates.
"""
from pathlib import Path
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/homicide_clean.csv"
REPORTS = ROOT / "reports"
FIGURES = ROOT / "figures"
YEARS = [2018, 2019, 2020, 2021, 2022]
AGE_ORDER = ["Under 18", "18–24", "25–34", "35–44", "45–54", "55–64", "65+", "Unknown"]
EXPECTED = {2018: 1738, 2019: 1665, 2020: 2178, 2021: 2338, 2022: 2187}
NAVY, TEAL, GREY, GRID = "#16324F", "#087E8B", "#CBD5E1", "#E4EBF0"


def source_summaries():
    df = pd.read_csv(DATA)
    required = {"source_csv_row", "incident_year", "victim_age_group", "county"}
    if missing := required.difference(df.columns):
        raise ValueError(f"Missing prepared columns: {sorted(missing)}")
    if len(df) != 10_106 or df["source_csv_row"].duplicated().any():
        raise ValueError("Prepared file failed record count/provenance validation")
    if df[list(required)].isna().any().any():
        raise ValueError("Missing analysis values")
    annual = df.groupby("incident_year").size().reindex(YEARS, fill_value=0)
    age = df.groupby("victim_age_group").size().reindex(AGE_ORDER, fill_value=0)
    county = df.groupby("county").size().sort_values(ascending=False)
    if df["victim_age_group"].isin(AGE_ORDER).sum() != len(df):
        raise ValueError("Unexpected age group")
    REPORTS.mkdir(exist_ok=True)
    annual.rename_axis("incident_year").reset_index(name="victim_records").to_csv(REPORTS / "annual_counts.csv", index=False)
    age.rename_axis("age_group").reset_index(name="victim_records").to_csv(REPORTS / "age_group_counts.csv", index=False)
    county.rename_axis("county").reset_index(name="victim_records").to_csv(REPORTS / "county_counts.csv", index=False)
    return annual, age, county


def tracked_summaries():
    annual = pd.read_csv(REPORTS / "annual_counts.csv").set_index("incident_year")["victim_records"]
    age = pd.read_csv(REPORTS / "age_group_counts.csv").set_index("age_group")["victim_records"]
    county = pd.read_csv(REPORTS / "county_counts.csv").set_index("county")["victim_records"]
    return annual, age, county


def validate(annual, age, county):
    if annual.to_dict() != EXPECTED:
        raise ValueError("Annual counts differ from audited source")
    if list(age.index) != AGE_ORDER or sum(age) != 10_106:
        raise ValueError("Age groups fail reconciliation")
    if len(county) != 56 or sum(county) != 10_106 or county.index[0] != "Los Angeles County":
        raise ValueError("County counts fail reconciliation")


def style(ax, grid_axis):
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis=grid_axis, color=GRID, linewidth=.85)
    ax.tick_params(length=0, labelcolor=NAVY, pad=8)
    axis = ax.yaxis if grid_axis == "y" else ax.xaxis
    axis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))


def save(fig, name):
    FIGURES.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(FIGURES / f"{name}.{ext}", dpi=190, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def plot_year(annual):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.subplots_adjust(left=.11, right=.965, bottom=.235, top=.76)
    fig.text(.11, .91, "CALIFORNIA HOMICIDE RECORDS  /  01", color=TEAL, fontsize=10, weight="bold")
    fig.text(.11, .83, "Reported victim records by incident year", color=NAVY, fontsize=19, weight="bold")
    ax.plot(annual.index, annual.values, color=TEAL, linewidth=3, marker="o", markersize=9, zorder=3)
    ax.set(xlim=(2017.75, 2022.25), ylim=(0, 2800), xticks=YEARS)
    ax.set_ylabel("Source victim records", color=NAVY, labelpad=14)
    style(ax, "y")
    for year, count in annual.items():
        ax.annotate(f"{count:,}", (year, count), xytext=(0, 13),
                    textcoords="offset points", ha="center", color=NAVY, weight="bold")
    fig.text(.11, .105, "California DOJ OpenJustice, 2018–2022. Counts, not rates or unique incidents.", fontsize=8.4, color="#718096")
    fig.text(.11, .073, "Note: 2021–2022 reporting-format transition limits direct comparisons across years.", fontsize=8.4, color="#718096")
    save(fig, "annual_victim_records")


def plot_bar(summary, name, title, subtitle, highlight, footnotes, left=.22):
    display = summary.iloc[::-1]
    fig, ax = plt.subplots(figsize=(10.8, 6.5))
    fig.subplots_adjust(left=left, right=.95, bottom=.21, top=.78)
    fig.text(left, .93, f"CALIFORNIA HOMICIDE RECORDS  /  {subtitle}", color=TEAL, fontsize=10, weight="bold")
    fig.text(left, .86, title, color=NAVY, fontsize=18.5, weight="bold")
    labels = [s.replace(" County", "") if name == "top_10_counties" else s for s in display.index]
    bars = ax.barh(labels, display.values,
                   color=[TEAL if x == highlight else GREY for x in display.index], height=.67)
    ax.set_xlim(0, summary.max() * 1.16)
    ax.set_xlabel("Source victim records", color=NAVY, labelpad=14)
    style(ax, "x")
    for bar, val in zip(bars, display.values):
        ax.text(val + 35, bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", color=NAVY, weight="bold", fontsize=9.5)
    for i, note in enumerate(footnotes):
        fig.text(left, .10 - i * .03, note, fontsize=8.4, color="#718096")
    save(fig, name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-summaries", action="store_true",
                        help="Regenerate figures from tracked aggregate CSVs, without source data")
    args = parser.parse_args()
    annual, age, county = tracked_summaries() if args.from_summaries else source_summaries()
    validate(annual, age, county)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "svg.fonttype": "none"})
    plot_year(annual)
    plot_bar(age, "age_group_victim_records", "Victim records by reported age group", "02",
             "25–34", [
                 "California DOJ OpenJustice, 2018–2022. Unknown age is shown separately.",
                 "Counts do not show age-specific risk; population denominators were not used."
             ], left=.20)
    plot_bar(county.head(10), "top_10_counties", "Counties with the largest recorded totals", "03",
             "Los Angeles County", [
                 "California DOJ OpenJustice, 2018–2022. County of reporting agency.",
                 "Counts are not adjusted for population or reporting completeness."
             ], left=.25)
    print("Created three figures from 10,106 audited source victim records.")


if __name__ == "__main__":
    main()

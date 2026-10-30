"""Compare DOJ's published county homicide counts with annual population size.

This is a descriptive, five-year pooled comparison, NOT a causal or individual-
risk analysis. Published DOJ counts are not replaced with archived source rows.

Uses DOJ Table 14 (2018–2022) and a locally checked DOF E-2 county/year CSV.
Run: python scripts/compare_published_county_ratios.py

Outputs under data/processed/ are local-only and Git-ignored.
"""
from pathlib import Path
import argparse
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.county_record_ratios import validate_population  # noqa: E402
from scripts.reconcile_doj_publication import validate_published  # noqa: E402

REFERENCE = ROOT / "reports/doj_published_table14_county_year.csv"
POPULATION = ROOT / "data/raw/county_population_2018_2022.csv"
CSV_OUTPUT = ROOT / "data/processed/published_county_pooled_2018_2022.csv"
PNG_OUTPUT = ROOT / "data/processed/published_count_vs_population_adjusted.png"
EXPECTED_POP_YEAR_TOTALS = {
    2018: 39_476_064,
    2019: 39_529_566,
    2020: 39_541_742,
    2021: 39_260_048,
    2022: 39_220_037,
}


def pooled_comparison(
    published: pd.DataFrame,
    population: pd.DataFrame,
    *,
    require_full_panel: bool = True,
) -> pd.DataFrame:
    """Compute a five-year pooled annualized COUNT/population descriptive ratio.

    Five-year ratio = (sum of 2018–22 published counts) /
                      (sum of 2018–22 July 1 county populations) * 100,000.

    The denominator approximates population-person-years; it is NOT a unique
    five-year population, and the numerator is NOT the archived record count.
    """
    published = validate_published(published, full_reference=require_full_panel)
    population = validate_population(
        population, require_full_state=require_full_panel
    )
    if require_full_panel:
        statewide = population.groupby("year")["population"].sum().to_dict()
        if statewide != EXPECTED_POP_YEAR_TOTALS:
            raise ValueError(
                f"DOF county populations do not reconcile to verified statewide totals: {statewide}"
            )
    joined = published.merge(
        population,
        on=["county", "year"],
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    if not joined["_merge"].eq("both").all():
        missing = joined.loc[
            joined["_merge"] != "both", ["county", "year"]
        ].head().to_dict("records")
        raise ValueError(f"Missing population county-years: {missing}")

    pooled = joined.groupby("county", as_index=False).agg(
        published_homicide_count=("published_homicide_crimes", "sum"),
        population_person_years=("population", "sum"),
        years_observed=("year", "nunique"),
    )
    if require_full_panel and not pooled["years_observed"].eq(5).all():
        raise ValueError("Each county must have five population observations")

    pooled["mean_annual_population"] = (
        pooled["population_person_years"] / pooled["years_observed"]
    ).round(0).astype("int64")
    pooled["annualized_count_per_100k"] = (
        100_000 * pooled["published_homicide_count"]
        / pooled["population_person_years"]
    ).round(2)

    if require_full_panel and pooled["published_homicide_count"].sum() != 10_187:
        raise ValueError("Published source counts do not reconcile to 10,187")

    return pooled.sort_values(
        ["mean_annual_population", "county"], ascending=[False, True]
    ).reset_index(drop=True)


def plot_comparison(pooled: pd.DataFrame, output: Path, top_n: int = 12) -> None:
    """Use the same top-population counties in both panels: no rate cherry-picking."""
    selected = pooled.head(top_n).iloc[::-1]
    labels = selected["county"].str.replace(" County", "", regex=False)
    y = range(len(selected))

    fig, (ax_count, ax_adjusted) = plt.subplots(
        ncols=2, figsize=(15, 8), sharey=True
    )
    fig.subplots_adjust(left=0.15, right=0.98, top=0.79, bottom=0.20, wspace=0.17)
    fig.suptitle(
        "California: published homicide counts and population adjustment",
        fontsize=17, fontweight="bold", color="#16324F", y=0.95
    )
    fig.text(
        0.15, 0.865,
        "Twelve counties with the largest mean population, 2018–2022",
        color="#475569", fontsize=11
    )

    for ax in (ax_count, ax_adjusted):
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(axis="x", alpha=0.2)
        ax.set_yticks(list(y), labels)

    ax_count.barh(y, selected["published_homicide_count"], color="#CBD5E1")
    ax_adjusted.barh(y, selected["annualized_count_per_100k"], color="#087E8B")
    ax_count.set_title("Published count across five years", fontsize=11)
    ax_adjusted.set_title("Annualized count per 100,000 residents", fontsize=11)
    ax_count.set_xlabel("Published homicide crimes, 2018–2022")
    ax_adjusted.set_xlabel("Published counts / population-person-years × 100,000")

    # Each row is the same county in both panels; avoid ranking by small-sample rate.
    for ax, numbers, fmt in [
        (ax_count, selected["published_homicide_count"], lambda x: f"{int(x):,}"),
        (ax_adjusted, selected["annualized_count_per_100k"], lambda x: f"{x:.2f}"),
    ]:
        ax.set_xlim(0, max(numbers) * 1.19 if max(numbers) else 1)
        for yy, value in enumerate(numbers):
            ax.text(value + ax.get_xlim()[1] * 0.015, yy, fmt(value),
                    va="center", fontsize=8.5, color="#16324F")

    fig.text(
        0.15, 0.095,
        "Sources: California DOJ Homicide in California 2022, Table 14; CA DOF E-2 July 1 county population.",
        fontsize=9, color="#64748B"
    )
    fig.text(
        0.15, 0.065,
        "Descriptive, not residence-based risk; 2018–19 and 2020–22 population series use different revisions.",
        fontsize=9, color="#64748B"
    )
    fig.text(
        0.15, 0.038,
        "Reporting changes in 2021–2022 limit comparisons. Five-year ratio uses the sum of annual populations.",
        fontsize=9, color="#64748B"
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population", type=Path, default=POPULATION)
    parser.add_argument("--table", type=Path, default=CSV_OUTPUT)
    parser.add_argument("--figure", type=Path, default=PNG_OUTPUT)
    args = parser.parse_args()

    if not args.population.is_file():
        parser.error(
            f"Missing population file {args.population}. "
            "Follow docs/population_denominators.md."
        )
    published = pd.read_csv(REFERENCE)
    population = pd.read_csv(args.population)
    pooled = pooled_comparison(published, population)

    args.table.parent.mkdir(parents=True, exist_ok=True)
    pooled.to_csv(args.table, index=False)
    plot_comparison(pooled, args.figure)

    print(f"Validated {len(pooled)} counties and 290 published county-years.")
    print(f"Published homicide count, 2018–2022: {pooled['published_homicide_count'].sum():,}")
    print(f"Wrote {args.table}")
    print(f"Wrote {args.figure}")
    print("\nLargest-population county sample (not selected by rate):")
    print(pooled.head(12)[[
        "county", "published_homicide_count", "annualized_count_per_100k"
    ]].to_string(index=False))
    print("\nThese are descriptive ratios, not comparable individual homicide risks.")


if __name__ == "__main__":
    main()

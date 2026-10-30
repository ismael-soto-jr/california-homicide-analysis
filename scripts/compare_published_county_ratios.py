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
plt.rcParams.update({'svg.fonttype': 'none', 'svg.hashsalt': 'california-doj-pooled-2018-2022'})
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.county_record_ratios import validate_population  # noqa: E402
from scripts.reconcile_doj_publication import validate_published  # noqa: E402

REFERENCE = ROOT / "reports/doj_published_table14_county_year.csv"
POPULATION = ROOT / "data/raw/county_population_2018_2022.csv"
CSV_OUTPUT = ROOT / "data/processed/published_county_pooled_2018_2022.csv"
PNG_OUTPUT = ROOT / "data/processed/published_count_vs_population_adjusted.png"
SVG_OUTPUT = ROOT / "figures/published_count_vs_population_adjusted.svg"
SUMMARY = ROOT / "reports/published_county_pooled_2018_2022.csv"
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


def plot_comparison(pooled: pd.DataFrame, output: Path, top_n: int = 12, svg_output: Path | None = None) -> None:
    """Use the same top-population counties in both panels: no rate cherry-picking."""
    selected = pooled.head(top_n).iloc[::-1]
    labels = selected["county"].str.replace(" County", "", regex=False)
    y = range(len(selected))

    fig, (ax_count, ax_adjusted) = plt.subplots(
        ncols=2, figsize=(15, 7.6), sharey=True
    )
    fig.subplots_adjust(left=.15, right=.97, top=.77, bottom=.18, wspace=.16)
    fig.suptitle(
        "How population adjustment changes county homicide comparisons",
        fontsize=17, fontweight="bold", color="#16324F", x=.15, ha="left", y=.96
    )
    fig.text(
        0.15, 0.865,
        "California’s 12 most populous counties, 2018–2022  ·  Ordered by average population (largest first)",
        color="#475569", fontsize=10.7
    )

    for ax in (ax_count, ax_adjusted):
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(axis="x", alpha=0.2)
        ax.set_yticks(list(y), labels)
        ax.tick_params(axis="y", length=0, pad=7)
        ax.tick_params(axis="x", labelsize=9)

    ax_count.barh(y, selected["published_homicide_count"], color="#CBD5E1", height=.8)
    ax_adjusted.barh(y, selected["annualized_count_per_100k"], color="#087E8B", height=.8)
    ax_count.set_title("Total published counts · five years", fontsize=11, pad=12)
    ax_adjusted.set_title("Annualized counts per 100,000 residents", fontsize=11, pad=12)
    ax_count.set_xlabel("Published homicide counts, 2018–2022", fontsize=10)
    ax_adjusted.set_xlabel("Five-year counts ÷ population-person-years × 100,000", fontsize=10)

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
        .15, .085,
        "Sources: California DOJ, Homicide in California 2022 (Table 14); CA DOF E-2 July 1 county populations.",
        fontsize=8.6, color="#64748B"
    )
    fig.text(
        .15, .052,
        "Descriptive only; reporting-county geography, 2021–22 reporting changes, and mixed population vintages limit comparison.",
        fontsize=8.6, color="#64748B"
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180, bbox_inches="tight", facecolor="white")
    if svg_output is not None:
        svg_output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(svg_output, bbox_inches="tight", facecolor="white", metadata={"Date": None})
    plt.close(fig)


def validate_published_summary(summary: pd.DataFrame) -> pd.DataFrame:
    """Ensure public pooled data agree with DOJ totals and own denominators."""
    expected = ["county", "published_homicide_count", "population_person_years",
                "years_observed", "mean_annual_population", "annualized_count_per_100k"]
    if list(summary.columns) != expected or len(summary) != 58:
        raise ValueError("Expected exactly 58 counties and standard published summary columns")
    if summary["county"].isna().any() or summary["county"].duplicated().any():
        raise ValueError("Pooled summary has missing or duplicate county names")
    numerical = expected[1:]
    if summary[numerical].isna().any().any():
        raise ValueError("Pooled summary contains missing numeric values")
    if not summary["years_observed"].eq(5).all():
        raise ValueError("Pooled summary must cover five years per county")
    if not summary["population_person_years"].gt(0).all():
        raise ValueError("Pooled summary has invalid denominators")
    if not summary["published_homicide_count"].ge(0).all():
        raise ValueError("Pooled summary has negative counts")
    if int(summary["published_homicide_count"].sum()) != 10_187:
        raise ValueError("Pooled summary published counts do not total 10,187")
    expected_ratios = (
        summary["published_homicide_count"] * 100_000 /
        summary["population_person_years"]
    ).round(2)
    if not (summary["annualized_count_per_100k"].round(2) == expected_ratios).all():
        raise ValueError("Published ratios do not reconcile with pooled county denominators")
    summary = summary.sort_values(
        ["mean_annual_population", "county"], ascending=[False, True]
    ).reset_index(drop=True)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population", type=Path, default=POPULATION)
    parser.add_argument("--from-summary", action="store_true",
                        help="Rebuild the chart from public pooled county summaries, without the local DOF spreadsheet")
    parser.add_argument("--svg", type=Path, default=SVG_OUTPUT)
    parser.add_argument("--table", type=Path, default=CSV_OUTPUT)
    parser.add_argument("--figure", type=Path, default=PNG_OUTPUT)
    args = parser.parse_args()

    if args.from_summary:
        pooled = validate_published_summary(pd.read_csv(SUMMARY))
    else:
        if not args.population.is_file():
            parser.error(
                f"Missing population file {args.population}. "
                "Follow docs/population_denominators.md, or use --from-summary."
            )
        published = pd.read_csv(REFERENCE)
        population = pd.read_csv(args.population)
        pooled = pooled_comparison(published, population)
        # Publish only a checked, derived aggregate of public-source figures.
        baseline = validate_published_summary(pd.read_csv(SUMMARY))
        comparison_cols = ["county", "published_homicide_count", "population_person_years",
                           "annualized_count_per_100k"]
        if not pooled[comparison_cols].equals(baseline[comparison_cols]):
            raise ValueError("Local results differ from the verified public pooled summary")

    args.table.parent.mkdir(parents=True, exist_ok=True)
    pooled.to_csv(args.table, index=False)
    plot_comparison(pooled, args.figure, svg_output=args.svg)
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

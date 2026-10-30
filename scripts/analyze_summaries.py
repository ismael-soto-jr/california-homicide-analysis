"""Compute descriptive composition from audited, published aggregate tables.

Run: python scripts/analyze_summaries.py
Check: python scripts/analyze_summaries.py --check

No individual-level DOJ inputs are needed. Shares are not population-based rates.
"""
from pathlib import Path
import argparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUTPUT = REPORTS / "composition_metrics.csv"
TOTAL = 10_106
YEARS = {2018: 1738, 2019: 1665, 2020: 2178, 2021: 2338, 2022: 2187}


def load_counts(filename: str, category_column: str) -> pd.Series:
    table = pd.read_csv(REPORTS / filename)
    if list(table.columns) != [category_column, "victim_records"]:
        raise ValueError(f"Unexpected columns in {filename}")
    if table[category_column].isna().any() or table[category_column].duplicated().any():
        raise ValueError(f"Missing or duplicate categories in {filename}")
    counts = pd.to_numeric(table["victim_records"], errors="raise")
    if counts.isna().any() or (counts < 0).any() or (counts % 1 != 0).any():
        raise ValueError(f"Invalid record counts in {filename}")
    return pd.Series(
        counts.to_numpy(dtype="int64"),
        index=table[category_column],
        name="victim_records",
    )


def calculate_metrics() -> pd.DataFrame:
    annual = load_counts("annual_counts.csv", "incident_year")
    age = load_counts("age_group_counts.csv", "age_group")
    county = load_counts("county_counts.csv", "county")
    if annual.to_dict() != YEARS or age.sum() != TOTAL or county.sum() != TOTAL:
        raise ValueError("Published aggregates do not reconcile with the audited sample")
    if len(county) != 56:
        raise ValueError("Unexpected number of counties represented in the extract")
    required_ages = {"18–24", "25–34", "35–44", "Unknown"}
    if not required_ages.issubset(set(age.index)):
        raise ValueError("Expected age groups are missing")
    county = county.sort_index().sort_values(ascending=False, kind="stable")
    if county.index[0] != "Los Angeles County":
        raise ValueError("Unexpected highest-count county")

    groups = [
        ("age", "Ages 18–44", int(age.loc[["18–24", "25–34", "35–44"]].sum())),
        ("age", "Ages 25–34", int(age.loc["25–34"])),
        ("age", "Unknown age", int(age.loc["Unknown"])),
        ("county", "Los Angeles County", int(county.loc["Los Angeles County"])),
        ("county", "Top 5 counties", int(county.iloc[:5].sum())),
        ("county", "Top 10 counties", int(county.iloc[:10].sum())),
    ]
    return pd.DataFrame(
        [
            {
                "dimension": dimension,
                "subset": subset,
                "victim_records": count,
                "share_pct": round(100 * count / TOTAL, 2),
            }
            for dimension, subset, count in groups
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true",
        help="Check that the published metrics CSV matches the source summaries",
    )
    args = parser.parse_args()
    expected_csv = calculate_metrics().to_csv(index=False, float_format="%.2f")
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected_csv:
            raise SystemExit("Composition metrics differ; run python scripts/analyze_summaries.py")
        print("Composition metrics match the audited aggregate summaries.")
    else:
        OUTPUT.write_text(expected_csv, encoding="utf-8")
        print(f"Wrote {OUTPUT.relative_to(ROOT)} from {TOTAL:,} source victim records.")


if __name__ == "__main__":
    main()

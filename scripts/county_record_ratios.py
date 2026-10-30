"""Prepare exploratory county-year recorded victim counts per 100,000 residents.

This is NOT an official homicide incidence-rate series. The numerator counts
historical DOJ victim source records by reporting-agency county and assault year;
population denominators are July 1 county resident estimates.

Requires a local, manually verified DOF population CSV with columns:
    county,year,population

Usage: python scripts/county_record_ratios.py
Raw inputs and record-level outputs are intentionally excluded from Git.
"""
from pathlib import Path
import argparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
YEARS = [2018, 2019, 2020, 2021, 2022]
EXPECTED_ANNUAL = {2018: 1738, 2019: 1665, 2020: 2178, 2021: 2338, 2022: 2187}
DEFAULT_POPULATION = ROOT / "data/raw/county_population_2018_2022.csv"
DEFAULT_RECORDS = ROOT / "data/processed/homicide_clean.csv"
DEFAULT_OUTPUT = ROOT / "data/processed/county_year_record_ratios.csv"


def validate_population(population: pd.DataFrame, *, require_full_state: bool = True) -> pd.DataFrame:
    """Verify a county-year crosswalk and strictly positive population totals."""
    required = {"county", "year", "population"}
    missing = required - set(population.columns)
    if missing:
        raise ValueError(f"Population data missing columns: {sorted(missing)}")

    result = population[list(("county", "year", "population"))].copy()
    if result.isna().any().any():
        raise ValueError("Population data contain missing values")

    result["county"] = result["county"].astype("string").str.strip()
    if result["county"].eq("").any() or not result["county"].str.endswith(" County").all():
        raise ValueError("Use full county names, e.g. 'Alameda County'")

    for col in ("year", "population"):
        numeric = pd.to_numeric(result[col], errors="coerce")
        if numeric.isna().any() or not (numeric % 1 == 0).all():
            raise ValueError(f"Population {col} must contain whole numbers")
        result[col] = numeric.astype("int64")

    if (result["population"] <= 0).any():
        raise ValueError("Population denominators must be strictly positive")
    if result.duplicated(["county", "year"]).any():
        raise ValueError("Duplicate county-year population records")
    if not result["year"].isin(YEARS).all():
        raise ValueError("Population years must be within 2018-2022")

    if require_full_state:
        if len(result) != 58 * len(YEARS):
            raise ValueError("Expected all 58 California counties in each of 5 years (290 rows)")
        counts = result.groupby("year")["county"].nunique().to_dict()
        if counts != {year: 58 for year in YEARS}:
            raise ValueError("Expected exactly 58 distinct California counties in every year")
    return result


def calculate_ratios(records: pd.DataFrame, population: pd.DataFrame) -> pd.DataFrame:
    """Count observed records and attach matched county-year denominators.

    County-years without observed records are NOT assumed to have zero homicides
    or complete reporting; they are absent from this output.
    """
    required = {"county", "incident_year", "source_csv_row"}
    missing = required - set(records.columns)
    if missing:
        raise ValueError(f"Prepared data missing columns: {sorted(missing)}")
    if records[list(required)].isna().any().any():
        raise ValueError("Prepared records contain missing key values")
    if records["source_csv_row"].duplicated().any():
        raise ValueError("Source-row identifiers are not unique")

    pop = validate_population(population, require_full_state=False).rename(
        columns={"year": "incident_year"}
    )
    counts = (
        records.groupby(["county", "incident_year"])
        .size()
        .reset_index(name="victim_records")
    )
    if not counts["incident_year"].isin(YEARS).all():
        raise ValueError("Prepared records include years outside the study period")

    result = counts.merge(
        pop, on=["county", "incident_year"], how="left",
        indicator=True, validate="one_to_one",
    )
    if not result["_merge"].eq("both").all():
        missing_keys = result.loc[
            result["_merge"] != "both", ["county", "incident_year"]
        ].to_dict("records")
        raise ValueError(f"County-year population missing for source records: {missing_keys[:5]}")

    result["recorded_victim_records_per_100k"] = (
        100_000 * result["victim_records"] / result["population"]
    ).round(2)
    return (
        result.drop(columns="_merge")
        .sort_values(["incident_year", "county"])
        .reset_index(drop=True)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population", type=Path, default=DEFAULT_POPULATION)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not args.population.exists():
        parser.error(f"Missing local population file: {args.population}. See docs/population_denominators.md")
    if not args.records.exists():
        parser.error(f"Missing cleaned records: {args.records}. Run python prepare_homicides.py first")

    population = validate_population(pd.read_csv(args.population))
    records = pd.read_csv(args.records)
    if len(records) != 10_106:
        raise ValueError("Prepared input differs from audited 10,106 source records")
    annual = records.groupby("incident_year").size().to_dict()
    if annual != EXPECTED_ANNUAL:
        raise ValueError("Source incident-year counts differ from the historical audit")

    ratios = calculate_ratios(records, population)
    if int(ratios["victim_records"].sum()) != 10_106:
        raise ValueError("County-year counts fail to reconcile with the source records")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    ratios.to_csv(args.output, index=False)
    print(f"Validated {len(ratios)} observed county-years; wrote {args.output}")
    print("Descriptive source-record ratios only; unobserved county-years are not coded as zero.")


if __name__ == "__main__":
    main()

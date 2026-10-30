"""Compare archived DOJ victim-source rows with published county-year counts.

Reference: California DOJ, Homicide in California 2022, Table 14 (pp. 19–20).
The reference represents reported homicide crimes / known victims.
The historical extract is a different publication/version; discrepancies are
diagnostic and must not be corrected by silently altering source records.

Run without archived data:
    python scripts/reconcile_doj_publication.py --check-reference

Run with the author's validated 2018–2022 source preparation:
    python scripts/reconcile_doj_publication.py
"""
from pathlib import Path
import argparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = ROOT / "reports/doj_published_table14_county_year.csv"
PREPARED = ROOT / "data/processed/homicide_clean.csv"
OUTPUT = ROOT / "data/processed/doj_county_reconciliation_2018_2022.csv"
ARCHIVE_TOTALS = {2018: 1738, 2019: 1665, 2020: 2178, 2021: 2338, 2022: 2187}
PUBLISHED_TOTALS = {2018: 1739, 2019: 1679, 2020: 2202, 2021: 2361, 2022: 2206}


def validate_published(reference: pd.DataFrame, *, full_reference: bool = True) -> pd.DataFrame:
    """Check published county/year keys and non-negative whole-number counts."""
    expected = ["county", "year", "published_homicide_crimes"]
    if list(reference.columns) != expected:
        raise ValueError(f"Expected published columns: {expected}")
    result = reference.copy()
    if result.isna().any().any():
        raise ValueError("Published table contains missing values")
    if not result["county"].astype(str).str.endswith(" County").all():
        raise ValueError("Published county names must end in ' County'")
    for column in ["year", "published_homicide_crimes"]:
        numeric = pd.to_numeric(result[column], errors="coerce")
        if numeric.isna().any() or (numeric % 1 != 0).any():
            raise ValueError(f"Published {column} values must be integers")
        result[column] = numeric.astype("int64")
    if (result["published_homicide_crimes"] < 0).any():
        raise ValueError("Published counts cannot be negative")
    if result.duplicated(["county", "year"]).any():
        raise ValueError("Duplicate county-year in published table")
    if not result["year"].isin(PUBLISHED_TOTALS).all():
        raise ValueError("Published years must be 2018–2022")

    if full_reference:
        counts = result.groupby("year")["county"].nunique().to_dict()
        if len(result) != 290 or counts != {year: 58 for year in PUBLISHED_TOTALS}:
            raise ValueError("Expected 58 counties for every study year (290 rows)")
        totals = result.groupby("year")["published_homicide_crimes"].sum().to_dict()
        if totals != PUBLISHED_TOTALS:
            raise ValueError(f"Published county sums differ from DOJ Table 14: {totals}")
    return result


def reconcile(
    records: pd.DataFrame,
    published: pd.DataFrame,
    *,
    full_reference: bool = True,
) -> pd.DataFrame:
    """Audit differences without interpreting absent archived rows as true zeros."""
    reference = validate_published(published, full_reference=full_reference)
    required = {"source_csv_row", "incident_year", "county"}
    if missing := required - set(records.columns):
        raise ValueError(f"Archived data missing columns: {sorted(missing)}")
    if records[list(required)].isna().any().any():
        raise ValueError("Archived records have missing keys")
    if records["source_csv_row"].duplicated().any():
        raise ValueError("Archived source-row identifiers are duplicated")
    if not records["incident_year"].isin(PUBLISHED_TOTALS).all():
        raise ValueError("Archived records contain unexpected years")

    counts = (
        records.groupby(["county", "incident_year"])
        .size()
        .rename("archived_victim_rows")
        .reset_index()
        .rename(columns={"incident_year": "year"})
    )
    # Prevent silently dropping any row if its county/year is not in Table 14.
    keys = counts.merge(
        reference[["county", "year"]],
        on=["county", "year"], how="left", indicator=True, validate="one_to_one"
    )
    if not keys["_merge"].eq("both").all():
        examples = keys.loc[keys["_merge"] != "both", ["county", "year"]].head().to_dict("records")
        raise ValueError(f"Archived county-year keys absent from reference: {examples}")

    table = reference.merge(counts, on=["county", "year"], how="left", validate="one_to_one")
    table["has_archived_victim_rows"] = table["archived_victim_rows"].notna()
    # Zero here means 'no rows in this extract', not verified zero crimes.
    table["archived_victim_rows"] = table["archived_victim_rows"].fillna(0).astype("int64")
    table["difference_rows_minus_published"] = (
        table["archived_victim_rows"] - table["published_homicide_crimes"]
    )
    table["source_row_status"] = table["has_archived_victim_rows"].map(
        {True: "Rows present", False: "No archived source rows; cannot infer true zero"}
    )
    return table.sort_values(["year", "county"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-reference", action="store_true",
                        help="Validate the public Table 14 transcription; no archived inputs needed")
    parser.add_argument("--records", type=Path, default=PREPARED)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    reference = validate_published(pd.read_csv(PUBLISHED))
    if args.check_reference:
        print("Published DOJ Table 14: 290 county-years; all five annual totals reconcile.")
        return

    if not args.records.exists():
        parser.error(f"Missing archived prepared data: {args.records}")
    records = pd.read_csv(args.records)
    if len(records) != 10_106:
        raise ValueError("Unexpected archived source-row count")
    annual = records.groupby("incident_year").size().to_dict()
    if annual != ARCHIVE_TOTALS:
        raise ValueError(f"Archived year totals differ from audit: {annual}")
    result = reconcile(records, reference)
    if result["archived_victim_rows"].sum() != 10_106:
        raise ValueError("Reconciliation lost archived records")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)

    summary = (
        result.groupby("year", as_index=False)
        .agg(archived_rows=("archived_victim_rows", "sum"),
             published_crimes=("published_homicide_crimes", "sum"),
             county_years_differing=("difference_rows_minus_published", lambda x: (x != 0).sum()))
    )
    summary["difference"] = summary["archived_rows"] - summary["published_crimes"]
    print("Annual archive-versus-publication reconciliation:")
    print(summary.to_string(index=False))
    print("\nLargest county-year differences (diagnostic, not corrections):")
    mismatches = result.loc[result["difference_rows_minus_published"] != 0].copy()
    mismatches["absolute_difference"] = mismatches["difference_rows_minus_published"].abs()
    columns = ["county", "year", "archived_victim_rows",
               "published_homicide_crimes", "difference_rows_minus_published"]
    print(mismatches.sort_values(["absolute_difference", "county", "year"],
                                 ascending=[False, True, True]).head(12)[columns].to_string(index=False))
    print(f"\nWrote {args.output} (local, Git-ignored).")
    print("Source differences remain unresolved; do not substitute published counts into the archival data.")


if __name__ == "__main__":
    main()

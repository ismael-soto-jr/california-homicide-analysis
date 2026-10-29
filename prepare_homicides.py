"""Prepare validated 2018–2022 California homicide source-victim records.

Run: python prepare_homicides.py
Output rows represent source records, not proven unique victims or incidents.
"""
from pathlib import Path
import argparse
import pandas as pd

ROOT = Path(__file__).resolve().parent
EXPECTED_YEARS = {2018: 1738, 2019: 1665, 2020: 2178, 2021: 2338, 2022: 2187}


def county_lookup(reference: pd.DataFrame) -> pd.DataFrame:
    required = {"CntyCode", "County"}
    if missing := required - set(reference.columns):
        raise ValueError(f"County reference missing columns: {sorted(missing)}")
    lookup = reference[["CntyCode", "County"]].drop_duplicates().copy()
    lookup["CntyCode"] = pd.to_numeric(lookup["CntyCode"], errors="raise").astype("Int64")
    lookup["County"] = lookup["County"].astype("string").str.strip()
    wrong = lookup["CntyCode"].eq(54) & lookup["County"].eq("Kings County")
    correct = lookup["CntyCode"].eq(54) & lookup["County"].eq("Tulare County")
    if wrong.any() and not correct.any():
        raise ValueError("County code 54 lacks its documented Tulare County mapping")
    lookup = lookup.loc[~wrong]
    if lookup.isna().any().any() or lookup["CntyCode"].duplicated().any():
        raise ValueError("Missing or ambiguous county lookup entries")
    codes = lookup.set_index("CntyCode")["County"]
    for code, name in {16: "Kings County", 54: "Tulare County"}.items():
        if codes.get(code) != name:
            raise ValueError(f"County code {code} must map to {name}")
    return lookup.rename(columns={"CntyCode": "county_code", "County": "county"})


def age_groups(raw: pd.Series) -> pd.Series:
    age = raw.astype("string").str.strip().str.upper()
    n = pd.to_numeric(age, errors="coerce")
    group = pd.Series("Unknown", index=raw.index, dtype="string")
    group.loc[age.isin(["NB", "BB"])] = "Under 18"
    for low, high, label in [
        (1, 17, "Under 18"), (18, 24, "18–24"), (25, 34, "25–34"),
        (35, 44, "35–44"), (45, 54, "45–54"), (55, 64, "55–64"),
        (65, 200, "65+"),
    ]:
        group.loc[n.between(low, high)] = label
    return group


def prepare(source: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    required = {"Inc YR", "Inc MO", "Inc day", "CO", "V age", "V sex", "V race", "Crm Stat"}
    if missing := required - set(source.columns):
        raise ValueError(f"Source data missing columns: {sorted(missing)}")
    years = pd.to_numeric(source["Inc YR"], errors="coerce")
    selected = source.loc[years.between(2018, 2022)].copy()
    # DOJ June 2023 codebook: 1 = actual/willful homicide;
    # 2/4 are justifiable homicides, 3 is manslaughter.
    if not selected["Crm Stat"].eq(1).all():
        raise ValueError("Study sample includes non-actual/willful homicide records")
    selected["source_csv_row"] = selected.index + 2
    selected["incident_year"] = years.loc[selected.index].astype(int)
    month = pd.to_numeric(selected["Inc MO"], errors="raise")
    day = pd.to_numeric(selected["Inc day"], errors="raise")
    if month.isna().any() or day.isna().any() or not month.between(1, 12).all():
        raise ValueError("Missing or invalid incident month/day")
    selected["incident_month"] = month.astype(int)
    selected["incident_date"] = pd.to_datetime(
        {"year": selected["incident_year"], "month": month, "day": day},
        errors="coerce",
    )
    if selected["incident_date"].isna().any():
        raise ValueError("Missing or invalid incident dates")
    selected["county_code"] = pd.to_numeric(selected["CO"], errors="raise").astype("Int64")
    selected["victim_age_code"] = selected["V age"].astype("string").str.strip()
    selected["victim_age_group"] = age_groups(selected["V age"])
    selected["victim_sex_code"] = pd.to_numeric(selected["V sex"], errors="raise").astype("Int64").astype("string")
    selected["victim_race_code"] = selected["V race"].astype("string")

    count_before = len(selected)
    selected = selected.merge(
        county_lookup(reference), on="county_code", how="left",
        validate="many_to_one", indicator=True, sort=False,
    )
    if len(selected) != count_before or not selected["_merge"].eq("both").all():
        raise ValueError("County lookup multiplied or failed to match records")
    cols = ["source_csv_row", "incident_date", "incident_year", "incident_month",
            "county_code", "county", "victim_age_code", "victim_age_group",
            "victim_sex_code", "victim_race_code"]
    result = selected[cols].sort_values("source_csv_row").reset_index(drop=True)
    if result["source_csv_row"].duplicated().any():
        raise ValueError("Source row provenance not unique")
    return result


def validate(source: pd.DataFrame, cleaned: pd.DataFrame) -> None:
    if len(source) != 88_930 or int(source.duplicated().sum()) != 6:
        raise ValueError("Original historical source count or duplicate audit changed")
    if cleaned["incident_year"].value_counts().sort_index().to_dict() != EXPECTED_YEARS:
        raise ValueError("Incident-year totals do not match historical audit")
    if len(cleaned) != 10_106 or cleaned["county"].eq("Tulare County").sum() != 161:
        raise ValueError("Analysis sample or Tulare County totals do not match audit")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "data/raw/HomicideActuals1987-2022.csv")
    parser.add_argument("--county-reference", type=Path, default=ROOT / "data/raw/NCIC Code Jurisdiction List_04242023.xlsx")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/homicide_clean.csv")
    args = parser.parse_args()
    source = pd.read_csv(args.source, low_memory=False)
    reference = pd.read_excel(args.county_reference)
    clean = prepare(source, reference)
    validate(source, clean)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(args.output, index=False)
    print(f"Validated {len(clean):,} source victim records; wrote {args.output}")


if __name__ == "__main__":
    main()

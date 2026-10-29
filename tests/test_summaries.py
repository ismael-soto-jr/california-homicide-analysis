"""Checks that published aggregates represent the audited source-record sample."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_published_summary_totals():
    annual = pd.read_csv(ROOT / "reports/annual_counts.csv")
    age = pd.read_csv(ROOT / "reports/age_group_counts.csv")
    county = pd.read_csv(ROOT / "reports/county_counts.csv")
    assert annual.set_index("incident_year")["victim_records"].to_dict() == {
        2018: 1738, 2019: 1665, 2020: 2178, 2021: 2338, 2022: 2187
    }
    assert annual["victim_records"].sum() == 10_106
    assert age["victim_records"].sum() == 10_106
    assert county["victim_records"].sum() == 10_106
    assert len(county) == 56
    assert age.loc[age["age_group"] == "25–34", "victim_records"].item() == 2754
    assert county.loc[county["county"] == "Los Angeles County", "victim_records"].item() == 3296

"""Synthetic regression checks; no historical source files required."""
import pandas as pd
import pytest
from prepare_homicides import prepare, county_lookup, age_groups


def reference():
    return pd.DataFrame({"CntyCode": [1, 1, 16, 54, 54],
                         "County": ["Alameda County", "Alameda County", "Kings County",
                                    "Tulare County", "Kings County"]})


def sample():
    return pd.DataFrame({
        "Inc YR": [2017, 2018, 2020, 2022, 2022],
        "Inc MO": [1, 2, 3, 4, 4],
        "Inc day": [5, 6, 7, 8, 8],
        "CO": [1, 54, 16, 54, 54],
        "V age": ["0", "NB", "25", "99", "99"],
        "V sex": [1, 2, 1, 0, 0],
        "V race": ["W", "B", "H", "X", "X"],
        "Crm Stat": [1, 1, 1, 1, 1],
    })


def test_row_preservation_and_county_merge():
    result = prepare(sample(), reference())
    assert len(result) == 4
    assert result["county"].tolist() == ["Tulare County", "Kings County", "Tulare County", "Tulare County"]
    assert result["source_csv_row"].tolist() == [3, 4, 5, 6]
    assert result["victim_sex_code"].tolist() == ["2", "1", "0", "0"]


def test_age_code_handling():
    assert age_groups(pd.Series(["0", "NB", "BB", "1", "17", "18", "99", None])).tolist() == [
        "Unknown", "Under 18", "Under 18", "Under 18", "Under 18", "18–24", "65+", "Unknown"
    ]


def test_ambiguous_county_mapping_rejected():
    ref = pd.concat([reference(), pd.DataFrame({"CntyCode": [1], "County": ["Other County"]})])
    with pytest.raises(ValueError, match="ambiguous"):
        county_lookup(ref)


def test_unmapped_county_rejected():
    s = sample()
    s.loc[1, "CO"] = 999
    with pytest.raises(ValueError, match="County lookup"):
        prepare(s, reference())


def test_invalid_incident_date_rejected():
    s = sample()
    s.loc[1, "Inc day"] = 32
    with pytest.raises(ValueError, match="incident dates"):
        prepare(s, reference())


def test_missing_canonical_county_code_rejected():
    with pytest.raises(ValueError, match="16 must map"):
        county_lookup(reference().query("CntyCode != 16"))


def test_non_willful_homicide_status_rejected():
    data = sample()
    data.loc[1, "Crm Stat"] = 2
    with pytest.raises(ValueError, match="non-actual/willful homicide"):
        prepare(data, reference())

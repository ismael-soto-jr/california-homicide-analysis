"""Data-free checks of published DOJ reference validation and reconciliation."""
import pandas as pd
import pytest

from scripts.reconcile_doj_publication import reconcile, validate_published


def publication():
    return pd.DataFrame({
        "county": ["Amador County", "Amador County", "Alpine County"],
        "year": [2019, 2020, 2020],
        "published_homicide_crimes": [1, 2, 0],
    })


def records():
    return pd.DataFrame({
        "source_csv_row": [2, 3, 4],
        "county": ["Amador County", "Amador County", "Amador County"],
        "incident_year": [2019, 2019, 2019],
    })


def test_partial_reference_not_accepted_as_full_published_table():
    with pytest.raises(ValueError, match="290 rows"):
        validate_published(publication())


def test_distinct_archived_rows_and_unobserved_keys_remain_explicit():
    compared = reconcile(records(), publication(), full_reference=False)
    amador19 = compared.query("county == 'Amador County' and year == 2019").iloc[0]
    amador20 = compared.query("county == 'Amador County' and year == 2020").iloc[0]
    alpine20 = compared.query("county == 'Alpine County' and year == 2020").iloc[0]
    assert amador19["archived_victim_rows"] == 3
    assert amador19["difference_rows_minus_published"] == 2
    assert bool(amador19["has_archived_victim_rows"])
    assert amador20["archived_victim_rows"] == 0
    assert amador20["difference_rows_minus_published"] == -2
    assert not bool(amador20["has_archived_victim_rows"])
    assert not bool(alpine20["has_archived_victim_rows"])


def test_duplicate_reference_county_year_rejected():
    ref = pd.concat([publication(), publication().iloc[[0]]])
    with pytest.raises(ValueError, match="Duplicate county-year"):
        validate_published(ref, full_reference=False)


def test_invalid_published_count_rejected():
    ref = publication()
    ref.loc[0, "published_homicide_crimes"] = -2
    with pytest.raises(ValueError, match="cannot be negative"):
        validate_published(ref, full_reference=False)


def test_archived_county_not_in_publication_rejected():
    rec = records()
    rec.loc[0, "county"] = "Imaginary County"
    with pytest.raises(ValueError, match="absent from reference"):
        reconcile(rec, publication(), full_reference=False)


def test_duplicated_archived_record_identifier_rejected():
    rec = records()
    rec.loc[1, "source_csv_row"] = 2
    with pytest.raises(ValueError, match="duplicated"):
        reconcile(rec, publication(), full_reference=False)

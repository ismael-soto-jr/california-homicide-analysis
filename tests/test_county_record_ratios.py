"""Synthetic validation tests for county-year descriptive population ratios."""
import pandas as pd
import pytest

from scripts.county_record_ratios import calculate_ratios, validate_population


def example_records():
    return pd.DataFrame({
        "source_csv_row": [2, 3, 4],
        "county": ["Alameda County", "Alameda County", "Napa County"],
        "incident_year": [2018, 2018, 2019],
    })


def example_population():
    return pd.DataFrame({
        "county": ["Alameda County", "Napa County", "Napa County"],
        "year": [2018, 2018, 2019],
        "population": [100_000, 48_000, 50_000],
    })


def test_ratios_use_matched_county_year_population():
    ratios = calculate_ratios(example_records(), example_population())
    assert ratios["victim_records"].tolist() == [2, 1]
    assert ratios["recorded_victim_records_per_100k"].tolist() == [2.0, 2.0]
    assert ratios["incident_year"].tolist() == [2018, 2019]


def test_unobserved_county_year_is_not_imputed_as_zero():
    ratios = calculate_ratios(example_records(), example_population())
    assert not ((ratios["county"] == "Napa County") & (ratios["incident_year"] == 2018)).any()


def test_missing_population_denominator_rejected():
    population = example_population().query("not (county == 'Napa County' and year == 2019)")
    with pytest.raises(ValueError, match="County-year population missing"):
        calculate_ratios(example_records(), population)


def test_duplicate_population_denominator_rejected():
    duplicate = pd.concat([example_population(), example_population().iloc[[0]]])
    with pytest.raises(ValueError, match="Duplicate county-year"):
        calculate_ratios(example_records(), duplicate)


def test_invalid_population_values_rejected():
    population = example_population()
    population.loc[0, "population"] = 0
    with pytest.raises(ValueError, match="strictly positive"):
        validate_population(population, require_full_state=False)


def test_incomplete_state_population_panel_rejected():
    with pytest.raises(ValueError, match="290 rows"):
        validate_population(example_population())


def test_noncanonical_county_names_rejected():
    population = example_population()
    population.loc[0, "county"] = "Alameda"
    with pytest.raises(ValueError, match="full county names"):
        validate_population(population, require_full_state=False)

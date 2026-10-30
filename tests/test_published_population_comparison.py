"""Self-contained tests for the DOJ Table 14 population comparison."""
import pandas as pd
import pytest
from pathlib import Path

from scripts.compare_published_county_ratios import pooled_comparison, plot_comparison, validate_published_summary


def published_sample():
    return pd.DataFrame({
        "county": ["Alameda County", "Alameda County", "Napa County", "Napa County"],
        "year": [2018, 2019, 2018, 2019],
        "published_homicide_crimes": [10, 20, 0, 5],
    })


def population_sample():
    return pd.DataFrame({
        "county": ["Alameda County", "Alameda County", "Napa County", "Napa County"],
        "year": [2018, 2019, 2018, 2019],
        "population": [100_000, 200_000, 50_000, 50_000],
    })


def test_pooled_ratio_uses_sum_of_annual_populations():
    out = pooled_comparison(
        published_sample(), population_sample(), require_full_panel=False
    )
    alameda = out.set_index("county").loc["Alameda County"]
    assert alameda["published_homicide_count"] == 30
    assert alameda["population_person_years"] == 300_000
    assert alameda["mean_annual_population"] == 150_000
    assert alameda["years_observed"] == 2
    assert alameda["annualized_count_per_100k"] == 10.0


def test_published_zero_count_retained_not_imputed():
    out = pooled_comparison(
        published_sample(), population_sample(), require_full_panel=False
    )
    napa = out.set_index("county").loc["Napa County"]
    assert napa["published_homicide_count"] == 5
    assert napa["population_person_years"] == 100_000
    assert napa["annualized_count_per_100k"] == 5.0


def test_missing_county_year_population_refused():
    pop = population_sample().iloc[:-1]
    with pytest.raises(ValueError, match="Missing population county-years"):
        pooled_comparison(published_sample(), pop, require_full_panel=False)


def test_duplicate_population_rows_refused():
    pop = pd.concat([population_sample(), population_sample().iloc[[0]]])
    with pytest.raises(ValueError, match="Duplicate county-year"):
        pooled_comparison(published_sample(), pop, require_full_panel=False)


def test_full_290_row_panel_required_for_production():
    with pytest.raises(ValueError, match="290 rows"):
        pooled_comparison(published_sample(), population_sample())


def test_comparison_figure_rendered(tmp_path):
    out = pooled_comparison(
        published_sample(), population_sample(), require_full_panel=False
    )
    png = tmp_path / "sample.png"
    plot_comparison(out, png, top_n=2)
    assert png.is_file()
    assert png.stat().st_size > 1_000


def test_published_pooled_summary_is_consistent():
    summary = pd.read_csv(Path(__file__).resolve().parents[1] / "reports/published_county_pooled_2018_2022.csv")
    validated = validate_published_summary(summary)
    assert len(validated) == 58
    assert validated["published_homicide_count"].sum() == 10_187
    assert validated.iloc[0]["county"] == "Los Angeles County"


def test_inconsistent_public_ratio_rejected():
    summary = pd.read_csv(Path(__file__).resolve().parents[1] / "reports/published_county_pooled_2018_2022.csv")
    summary.loc[0, "annualized_count_per_100k"] = 99
    with pytest.raises(ValueError, match="ratios do not reconcile"):
        validate_published_summary(summary)

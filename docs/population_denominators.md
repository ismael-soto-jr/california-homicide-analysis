# County-year population denominators: exploratory extension

**Status:** Analysis code and synthetic tests are prepared. **No county-year rates are published in this repository** until population inputs and reporting comparability have been checked.

## Research question

How do *recorded* California DOJ actual/willful homicide victim-source-row counts compare with the population of the county of the reporting agency for each year from 2018 through 2022?

The resulting measure is **recorded victim-source rows per 100,000 county residents**. It should **not** be presented as an official homicide incidence rate, an estimate of individual risk, or evidence of causal effects.

## Population sources to obtain

Use California Department of Finance **E-2 July 1 county population estimates**, rather than Census ACS 5-year rolling estimates, as annual denominators:

1. [Historical E-2 July 1, 2010–2019](https://dof.ca.gov/Forecasting/Demographics/Estimates/) — extract **2018** and **2019**.
2. [E-2 July 1, 2020–2025](https://dof.ca.gov/forecasting/demographics/estimates/E-2/) — extract **2020**, **2021**, **2022**.

Keep the original Excel files locally and document their dates, versions, and county definitions. The two E-2 periods may reflect **different revisions/benchmarks around the 2020 Census**; verify the continuity before interpreting changes in calculated ratios. For a cross-check, California DWR's [county/DAU population trend dataset](https://publish.data.ca.gov/dataset/california-population-trends-by-geography) includes July county population totals based on DOF data over the same years; that dataset aggregates across DAUs and should not be mixed into E-2 without checking comparability.

## Required local population table

Convert the E-2 county totals to a local CSV at:

`data/raw/county_population_2018_2022.csv`

with the **exact** column headers:

```csv
county,year,population
```

Formatting requirements:

- One county-year per row: **58 counties × 5 years = 290 rows**.
- Use canonical county names with the ` County` suffix, such as `Alameda County`.
- `year` must be an integer 2018 through 2022.
- `population` must be a **positive whole number without commas**.
- Exclude California statewide totals, incorporated cities, unincorporated areas, and subtotals.
- Never infer missing annual population estimates, substitute adjacent years, or add county-year zeros to the homicide data.
- **Do not edit or overwrite** the archived original population workbooks.

The population CSV is excluded by `.gitignore`. Store the input provenance in your research notes even when the underlying population estimates are openly available.

## Run on the author's full historical data

First process the archived DOJ source and county lookup:

```bash
python prepare_homicides.py
```

After preparing and validating the 290-row population file:

```bash
python scripts/county_record_ratios.py
```

The script writes a **local-only**, Git-ignored CSV:

`data/processed/county_year_record_ratios.csv`

Columns: `county`, `incident_year`, `victim_records`, `population`, and `recorded_victim_records_per_100k`.

It validates the original 10,106-row sample and its year totals, checks unique county-year population values, enforces positive denominators, matches on county **and year**, and checks that every observed victim-source record is included once.

To run **synthetic tests without any DOJ or population inputs**:

```bash
python -m pytest -q tests/test_county_record_ratios.py
```

### Interpretation and coverage safeguards

- DOJ county codes describe the **county of the reporting law enforcement agency**, which is not necessarily the victim's county of residence.
- The study years refer to the recorded **assault** date, not necessarily the death date.
- DOJ states that its **2021–2022** records combine summary and incident-based reporting; differences across these years may reflect reporting changes.
- Historical source victim rows do not necessarily represent unique victims or incidents. Six exact source-row matches were retained where identification was ambiguous.
- Only **56 counties** occur in the selected five-year numerator extract, while the population file should cover all **58 California counties**. Counties/years without a reported victim row are **not assigned zero**: a missing record could reflect non-reporting or zero observed occurrences. Reporting coverage requires external verification.
- A ratio based on the population of the reporting county is **not a residence-based risk rate**. Population adjustment alone does not establish comparable risks across counties.
- Small annual counts can produce volatile ratios; consider multi-year pooling, uncertainty, and reporting completeness before drawing conclusions.

Before publishing any tables, charts, rankings, or conclusions from the computed local ratios, verify the denominator provenance and the DOJ reporting definition/coverage for each county-year.

## Sources

- California Department of Finance, [Population Estimates](https://dof.ca.gov/Forecasting/Demographics/Estimates/) and [E-2 July 1, 2020–2025](https://dof.ca.gov/forecasting/demographics/estimates/E-2/).
- California DOJ Criminal Justice Statistics Center, [June 2023 Homicide File Context](https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2023-06/Homicide%20Context_06122023.pdf).

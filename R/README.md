# R demo: published California homicide counts and population adjustment

This is a **self-contained, public-aggregate-data R demonstration** alongside the main Python research portfolio. It revisits the core workflow from the older `California_homicides/Data_Analysis_Full_Example` R Markdown notebooks: validate sources, aggregate reported homicide counts, join population denominators, calculate a per-100,000 measure, and visualize the comparison.

**Important distinction:** The earlier notebook used IPUMS USA microdata (`PERWT`) and historical Supplementary Homicide Reports to estimate 2019–2020 demographic-specific rates. This demo uses a *different, audited California-only dataset*: DOJ's **published Table 14 county-year homicide-crime counts (2018–2022)** and California Department of Finance **E-2 county population estimates**. It does **not** reproduce the old demographic rates, copy the old 2019-to-2020 population assumption, or use the archived DOJ record-level 10,106-row dataset.

## Why the source inputs are reproducible

Two existing, tracked repository tables are sufficient:

- [DOJ published county-year counts](../reports/doj_published_table14_county_year.csv): 58 counties × 5 years = **290 observations**, totaling **10,187** published counts.
- [Audited pooled county population and count table](../reports/published_county_pooled_2018_2022.csv): 58 counties; county-specific sums of five July 1 populations (**population-person-years**), plus published count and ratio references.

The second table is an **already-derived, audited aggregate**, not a fresh download of the original annual DOF spreadsheets. Consequently, this demo independently reconstructs counts from the annual published DOJ table and recomputes the pooled ratios from the preserved population-person-year totals. It **does not independently rebuild the population denominators from original annual DOF workbooks**. The full annual county-year join and provenance checks are implemented in the [Python comparison workflow](../scripts/compare_published_county_ratios.py) and explained in [population documentation](../docs/published_county_population_comparison.md).

## Formula

For each county, the annualized five-year pooled descriptive count ratio is:

```text
  Sum of published DOJ counts, 2018–2022
  -------------------------------------- × 100,000
  Sum of county populations, 2018–2022
```

The denominator is approximately five years of population exposure, **not** the 2022 population or the number of unique people over five years. Dividing a five-year total by a single year's population would substantially overstate the annualized measure.

## Run locally

From the repository root with R installed:

```bash
Rscript -e 'install.packages(c("dplyr", "readr", "ggplot2"), repos="https://cloud.r-project.org")'
Rscript R/tests/test_pooled_count_ratio_demo.R
Rscript R/pooled_count_ratio_demo.R
```

Outputs:

- `data/processed/r_published_county_pooled_2018_2022.csv` — independently recalculated 58-county table; local output, excluded from Git
- `figures/r_published_count_vs_population_adjusted.png` — two-panel comparison for the 12 most populous counties, selected **by population**, not by count or rate

The synthetic tests require **no raw data**, and verify both expected ratios and failures on duplicated keys, mismatched reported totals, and invalid denominators. The production script also checks year coverage, 58 county keys, positive denominators, a 10,187-count statewide total, and exact agreement with the published aggregate ratios.

## Interpretive limits

- DOJ counts are reported by **county of the reporting law-enforcement agency**, not necessarily victims' county of residence.
- DOJ reporting changed in 2021–2022, affecting cross-year comparability.
- Population denominators combine historical 2018–2019 and revised 2020–2022 DOF E-2 estimate releases, which may have a vintage discontinuity.
- These are **descriptive published-count-to-population ratios**, not causal estimates, verified unique-victim risk rates, or official risk rankings.
- Small-area annual comparisons can be unstable. The plot limits its display to 12 counties selected for population size; the calculation still covers all 58 counties.

## Possible next extension: demographic rates

A separate R demonstration could reconstruct the original Census/SHR logic once its source definitions and reporting coverage are audited. That would involve IPUMS `PERWT` by state, year, age group, sex, and harmonized race/ethnicity; validation of homicide-victim definitions and missing categories; joining only on consistent demographic keys; and explicitly documenting 2020 population estimates. It should not be mixed into this California DOJ/DOF pooled-county example.

**Original source workflow:** [homicide_data_preparation.Rmd](https://github.com/ismael-soto-jr/California_homicides/blob/main/Data_Analysis_Full_Example/homicide_data_preparation.Rmd) (private older repository).

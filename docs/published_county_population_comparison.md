# Exploratory population-adjusted comparison of published county counts (2018–2022)

## Research question

How does the geographic distribution of California's *published reported homicide counts* compare with county population sizes?

This extension intentionally uses the **published DOJ Table 14 county-year counts** rather than the historical archived victim-source records. Their known differences are documented in [source reconciliation](doj_publication_reconciliation.md). This does **not** resolve those discrepancies or turn the archived records into official rates.

## Data sources and interpretation

- **Numerators:** California DOJ, [*Homicide in California 2022*, Table 14](https://data-openjustice.doj.ca.gov/sites/default/files/2023-06/Homicide%20In%20CA%202022f.pdf), 58 county-year homicide-crime counts from 2018 to 2022; the verified source transcription is [here](../reports/doj_published_table14_county_year.csv). The report says its homicide-crime counts represent known victims.
- **Denominators:** California Department of Finance [E-2 July 1 county population estimates](https://dof.ca.gov/Forecasting/Demographics/Estimates/). The prepared local CSV combines **2018–2019** from an older 2010–2019 E-2 release and **2020–2022** from a revised February 2026 2020–2025 E-2 release.
- **Geography:** DOJ reports by **county of the reporting law-enforcement agency**; DOF measures **county residents**. These are not necessarily the same population at risk.
- **Time:** Five-year pooled totals reduce isolated annual fluctuations, but do not remove the 2021–2022 crime reporting transition or other reporting differences.

### Calculation

For each county:

```text
Published 2018–2022 homicide-crime count
------------------------------------------------------ × 100,000
Sum of July 1 county populations, 2018 through 2022
```

The denominator approximates **population-person-years** and is the correct scaling for an *annualized, five-year pooled descriptive count ratio*. A five-year count divided by a **single-year** population would overstate an annual rate by roughly a factor of five.

These are **published counts per 100,000 county residents annually, averaged across five years**. They are not person-level homicide probabilities, residence-based rates, adjusted causal effects, or evidence that one county is intrinsically safer than another.

## Verified population totals (input provenance checks)

| DOF July 1 year | 58-county population total | Estimate series |
| --- | ---: | --- |
| 2018 | 39,476,064 | Historical 2010–2019 release |
| 2019 | 39,529,566 | Historical 2010–2019 release |
| 2020 | 39,541,742 | Revised 2020–2025 E-2 (February 2026) |
| 2021 | 39,260,048 | Revised 2020–2025 E-2 (February 2026) |
| 2022 | 39,220,037 | Revised 2020–2025 E-2 (February 2026) |

The script rejects population inputs that do not contain exactly **290 complete county-years**, valid integer populations, and these five separately verified statewide totals. Mixing vintages may introduce a discontinuity around the 2020 Census even after validation. See [population denominator notes](population_denominators.md).

## Reproduce locally

With the original checked DOF extracts transformed into a local, Git-ignored file at `data/raw/county_population_2018_2022.csv`:

```bash
python -m pytest -q
python scripts/compare_published_county_ratios.py
```

The script creates two **local-only** outputs:

- `data/processed/published_county_pooled_2018_2022.csv`: all 58 county-level five-year published counts, estimated population-person-years, mean population, and annualized count ratio.
- `data/processed/published_count_vs_population_adjusted.png`: a side-by-side chart using the **same 12 largest-population counties** in both panels.

The 12 counties are chosen by **mean annual population**, not by the resulting population-adjusted ratio. This avoids disproportionately emphasizing small counties with volatile ratios. Neither the CSV nor the PNG is committed to GitHub before reviewing the empirical output.

## How to interpret the visualization

Two ways of describing an area's records can lead to different-looking comparisons: absolute reported counts and reported counts scaled by resident population. A higher population-adjusted number does **not** automatically imply higher individual homicide risk, especially where reporting coverage or residence geography differs.

Avoid drawing time-trend conclusions from the pooled comparison: the figure does not estimate separate annual changes or test differences between years. Results use mixed-vintage population estimates (2018–19 versus 2020–22), and DOJ reporting changed in 2021–22.

The final chart and empirical numbers should be visually inspected and matched against the table before anyone presents them in an application, resume, presentation, or article.

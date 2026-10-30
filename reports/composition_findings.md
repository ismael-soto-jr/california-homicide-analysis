# Additional descriptive analysis: age composition and county concentration

**Source:** Audited 2018–2022 California DOJ OpenJustice historical homicide extract (downloaded August 2023)  
**Unit:** Source victim records classified as actual/willful homicide, **not** proven distinct incidents  
**Denominator for all shares below:** 10,106 source victim records

This extension uses only the three public, audited aggregate tables. It illustrates **composition of reported records**, not population-adjusted homicide risk.

## Results

| Measure | Source victim records | Share of all 10,106 records |
| --- | ---: | ---: |
| Ages 18–44 (three combined reported age bands) | 6,738 | 66.67% |
| Ages 25–34 | 2,754 | 27.25% |
| Unknown age | 53 | 0.52% |
| Los Angeles County | 3,296 | 32.61% |
| Five counties with the most records | 5,852 | 57.91% |
| Ten counties with the most records | 7,782 | 77.00% |

The 18–44 total combines the **18–24**, **25–34**, and **35–44** categories from the audited age-group table. The county subtotals rank the 56 counties appearing in the historical data, using consistent alphabetical ordering for tied counts. These groups overlap: for example, Los Angeles County is included in the top-five and top-ten totals; rows of this table should **not** be added together.

## Interpretation

**Age composition:** About two-thirds of the selected victim records fall in the reported ages 18–44. This describes the composition of the *records*, not whether people ages 18–44 faced higher homicide risk. Measuring risk requires age-specific population denominators and careful comparison of source definitions.

**County concentration:** The ten counties with the largest recorded totals account for 77.00% of the statewide selected records. This does **not** establish that these counties have the highest homicide rates or that they are more dangerous. Counts are influenced by county population size, the county assigned to reporting agencies, and reporting differences. The sample contains records from **56 counties**, not a denominator suitable for comparing all 58 California counties' risk.

**Temporal scope:** These are pooled 2018–2022 records from a frozen extract downloaded in August 2023. DOJ reporting changes in 2021–2022 limit interpretation of year-to-year differences.

## Reproduce

From the repository root after installing `requirements.txt`:

```bash
python scripts/analyze_summaries.py
python scripts/analyze_summaries.py --check
```

The first command generates [`composition_metrics.csv`](composition_metrics.csv). The second verifies that the tracked metrics exactly match the three aggregate tables:

- [Annual counts](annual_counts.csv)
- [Age-group counts](age_group_counts.csv)
- [County counts](county_counts.csv)

No original individual-level source files are required for this analysis, so these metrics can be reproduced publicly. **This check does not independently verify the original source-record cleaning**, which requires the archived DOJ extract and county crosswalk; see [data access notes](../docs/data_access.md) and [validation results](validation_results.md).

## Next methodological step

To make defensible **population-adjusted comparisons**, obtain compatible county-year population estimates, identify reporting coverage across county-years, reconcile geographic definitions, and document how the 2021–2022 reporting transition affects comparability. Until then, interpret all results as descriptive counts and shares.

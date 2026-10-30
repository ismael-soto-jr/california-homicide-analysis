# California homicide records: preparation validation

**Historical extract:** California DOJ OpenJustice homicide source, downloaded August 2023  
**Study years:** 2018–2022  
**Original detailed audit:** Executed locally against the archived source CSV and NCIC workbook on October 28, 2026.  
**Local reproduction:** The full preparation and figure-generation scripts ran successfully again on October 29, 2026, validating 10,106 records. The existing eight-test suite also passed locally.  
**CI:** GitHub Actions independently runs the data-free preparation tests and rebuilds charts from published aggregate tables.

## Results

| Check | Result |
| --- | ---: |
| Source CSV rows | 88,930 |
| Selected source victim records, 2018–2022 | 10,106 |
| Annual record totals match audited benchmarks | Pass |
| Exact matching source rows beyond first copies, retained | 6 |
| County merge changes row count | No |
| Records with county code 54 assigned to Tulare County | 161 |
| Counties represented in selected data | 56 |
| Missing/invalid incident dates | 0 |
| Missing county labels after merge | 0 |
| Recorded age group `Unknown` | 53 |
| Missing victim sex code | 1 |
| Missing victim race code | 0 |
| Automated tests (preparation and published summaries) | 8 passed locally (October 29, 2026) |

### Annual counts

| Incident year | Source victim records |
| --- | ---: |
| 2018 | 1,738 |
| 2019 | 1,665 |
| 2020 | 2,178 |
| 2021 | 2,338 |
| 2022 | 2,187 |
| **Total** | **10,106** |

## Output schema

The prepared CSV has 10 columns: `source_csv_row`, `incident_date`, `incident_year`, `incident_month`, `county_code`, `county`, `victim_age_code`, `victim_age_group`, `victim_sex_code`, and `victim_race_code`.

- `source_csv_row`: 1-based row position in the original CSV, including its header row.
- `victim_sex_code`: original numeric codes without decimal suffix, with unknowns left missing.
- `victim_race_code`: source-coded value; race/ethnicity labeling is deferred pending codebook verification.
- `victim_age_group`: broad grouping distinguishing unknown code `0` from infant codes `NB`/`BB`.

## Interpretive cautions

Each row is a **source victim record**, not necessarily a unique victim or homicide incident. The six identical source rows are retained because missing identifiers do not establish whether they are duplicated persons. These are raw record counts, not population-adjusted incidence rates; trends may be affected by changes in reporting systems in 2021–2022.

## Reproducibility and distribution

All **eight automated tests** (seven preparation tests using synthetic inputs and one published-aggregate consistency test) can run in GitHub Actions without archived source files. The full historical-data validation was separately run locally against the original CSV and Excel workbook; these original files and the cleaned record-level CSV are excluded from Git pending source-version and redistribution review.

A separate [descriptive composition analysis](composition_findings.md) calculates age-group and county concentration shares from the audited public summary tables. Run `python scripts/analyze_summaries.py --check` to verify that the derived [metrics CSV](composition_metrics.csv) matches those summaries. This public-data check is **not** a substitute for rebuilding the individual-level dataset from archived inputs.

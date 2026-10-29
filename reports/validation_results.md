# California homicide records: preparation validation

**Historical extract:** California DOJ OpenJustice homicide source, downloaded August 2023  
**Study years:** 2018–2022  
**Validation:** Executed locally against the user-supplied CSV and NCIC workbook on October 28, 2026.

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
| Synthetic regression tests | 6 passed |

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

The **six synthetic tests** can run in GitHub Actions without input files. The full historical-data validation was run locally against the original CSV and Excel workbook. They and the derived CSV are deliberately excluded from Git until redistribution rights are reviewed.

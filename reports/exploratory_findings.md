# Exploratory descriptive findings: California homicide records, 2018–2022

**Source:** California DOJ Criminal Justice Statistics Center, historical OpenJustice homicide extract downloaded August 2023. Interpret fields using the June 2023 *Homicide File Context* ([codebook notes](../docs/source_codebook.md)).  
**Analysis unit:** source victim records with crime status 1 (actual/willful homicide); not unique incidents or population-adjusted rates.

## Figure 1 — Annual victim-record counts

![Annual reported victim records](../figures/annual_victim_records.svg)

| Year of incident (assault) | Source victim records |
| --- | ---: |
| 2018 | 1,738 |
| 2019 | 1,665 |
| 2020 | 2,178 |
| 2021 | 2,338 |
| 2022 | 2,187 |
| **Total** | **10,106** |

**Finding:** The highest annual record count is 2,338 in 2021, followed by 2,187 in 2022. These counts cannot establish year-to-year changes in homicide risk or their causes, especially because DOJ warns that 2021–2022 combined different reporting formats.

## Figure 2 — Recorded age distribution

![Source victim records by age group](../figures/age_group_victim_records.svg)

**Finding:** Ages **25–34** represent **2,754 records (27.3%)**, the largest broad category in this extract. Age was unknown for **53 records**. The analysis avoids equating higher counts with greater individual risk because age-group populations were not included. DOJ age code `0` means unknown; `NB` and `BB` are infants, and `99` means age 99 or older.

## Figure 3 — Top 10 counties by recorded count

![Top counties by source victim records](../figures/top_10_counties.svg)

**Finding:** **Los Angeles County** has **3,296 records (32.6% of the statewide selected total)**. The next largest count is **San Bernardino County (812)**. This largely reflects raw case volume: county populations, reporting completeness, and other differences have **not** been controlled for. County is defined as the county of the *reporting law-enforcement agency*.

## Research practice / reproducibility

1. Regenerate the validated 10,106-row sample from original inputs with `python prepare_homicides.py`.
2. Run `python scripts/build_figures.py` to generate these three figures and three aggregate tables from the processed dataset.
3. Alternatively, run `python scripts/build_figures.py --from-summaries` to reproduce equivalent graphics using the three published aggregate CSV tables, without the restricted raw inputs.
4. All three tables sum to **10,106 source records**, and regression tests check expected yearly, age, and county totals.

The SVG previews in the repository are based on these checked aggregate tables; the Matplotlib script generates publication-ready PNG and SVG versions from the same totals.

## Key limitations

- DOJ indicates that its 2021–2022 data combined summary and incident-based reporting; direct year comparisons require caution.
- `incident_date` is the date of the **assault** ultimately causing death, not necessarily the date of death.
- Source victim records do not necessarily correspond one-to-one with unique incidents.
- Six exact source-row matches were retained because missing identifiers do not establish whether they represent duplicate people.
- The downloaded file does not necessarily contain every person represented in DOJ published totals (including the DOJ's stated exclusion of two non-binary victims in its 2022 publication).
- Raw counts by county or demographic group should not be interpreted as differences in population-adjusted homicide risk.

This is **descriptive exploratory research**, not causal analysis.

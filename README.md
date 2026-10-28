# California Homicides | Data Preparation (2018–2022)

**Python · pandas · quality assurance · reproducible research**

A focused research-analyst portfolio project documenting the preparation of California Department of Justice OpenJustice homicide data. This is **Phase 1: cleaning and validation**; visualizations and substantive descriptive analysis will be added after the cleaned file is checked.

## The workflow

1. Read the original 1987–2022 historical California DOJ source extract and a county-code reference workbook.
2. Keep records with incident year 2018–2022 without automatically deleting identical rows.
3. Correct the documented county-code conflict (54 = Tulare County, not Kings County), then merge with many-to-one validation.
4. Construct incident dates, preserve original age/sex/race codes, and categorize recorded age (with special handling for unknown age and infant codes).
5. Check the output against historical record-count benchmarks before writing a clean analysis CSV.

The original methodological audit documented **88,930 source rows**, **10,106 records from 2018–2022**, **six ambiguous exact-row matches retained**, and **161 records coded to Tulare County**. These figures are checks against the historical extract, not claims about distinct homicide incidents or independently verified victims. The standalone script still requires testing against the original CSV and workbook.

## Repository guide

- `prepare_homicides.py` — single, readable, reusable Python pipeline.
- `tests/test_prepare.py` — synthetic regression tests, no source data needed.
- `requirements.txt` — Python dependencies.
- `data/raw/` — input files (kept outside Git until redistribution terms are reviewed).
- `data/processed/` — generated `homicide_clean.csv` (not tracked).

## Required input files

Place these exact files under `data/raw/`:

- `HomicideActuals1987-2022.csv`
- `NCIC Code Jurisdiction List_04242023.xlsx`

They are in the original private `California_homicides` repository. Source: [California DOJ OpenJustice](https://openjustice.doj.ca.gov/data); historical extract downloaded in August 2023. Do not publish source inputs without reviewing redistribution and licensing conditions.

## Reproduce

From the repository root, using Python 3.11 or a compatible version:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python prepare_homicides.py
```

After validation, the pipeline writes `data/processed/homicide_clean.csv`. It stops on unexpected source counts, ambiguous county codes, invalid incident dates, or merge mismatches.

## Interpretation

Records in this project are **source victim records**, not necessarily unique people or homicide incidents. They are **not population-adjusted rates**, and this is not a causal study. Six identical rows with unavailable identifiers are retained conservatively. Changing reporting systems during 2021–2022 can complicate comparisons. The original sex/race codes remain untranslated until verified against DOJ documentation.

## Author

Ismael Soto Jr. — Master of Public Policy and Graduate Certificate in Applied Data Science, UC Berkeley.

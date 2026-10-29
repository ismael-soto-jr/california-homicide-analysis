# California Homicide Data Preparation (2018–2022)

**Research analyst portfolio project · Python · pandas · data validation**

A compact, auditable workflow that turns a historical California Department of Justice (DOJ) OpenJustice extract into a cleaned dataset for descriptive analysis. This repository intentionally focuses on **Phase 1: source-data preparation**, before creating charts or drawing substantive conclusions.

## Project structure

| File or directory | Purpose |
| --- | --- |
| `prepare_homicides.py` | Filter, clean, check county merges, and export analysis-ready records |
| `tests/test_prepare.py` | Synthetic regression tests that don't require the source datasets |
| `requirements.txt` | Python dependencies |
| `data/raw/` | Local source files; ignored by Git until sharing rights are reviewed |
| `data/processed/` | Generated CSV; ignored by Git |
| `.gitignore` | Excludes source data, generated data, and local machine files |

## Required source files

Place these two files in `data/raw/`, using their original filenames:

- `HomicideActuals1987-2022.csv` — historical California DOJ OpenJustice homicide extract downloaded in August 2023.
- `NCIC Code Jurisdiction List_04242023.xlsx` — county/agency reference workbook.

They are retained in the original **private** `California_homicides` repository. Do not republish the raw files until their redistribution terms are confirmed.

## Reproduce

From the repository root, using a compatible Python installation (Python 3.11 recommended):

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python prepare_homicides.py
```

The script writes `data/processed/homicide_clean.csv` after all expected-count checks pass.

## What is checked

- Restrict to incident years **2018–2022**, keeping original source-row identifiers.
- Preserve exact duplicate rows rather than assuming they refer to duplicate people.
- Correct a documented reference workbook error: **county code 54 maps to Tulare County, not Kings County**; code **16 maps to Kings County**.
- Require a **many-to-one county merge** so reference data cannot multiply source rows.
- Validate incident dates and preserve original sex/race codes without undocumented relabeling.
- Create broad age groups that distinguish coded infants from unknown ages.
- Assert source-record and annual-count benchmarks from the previous methodological audit.

The older audit reported **88,930 source rows** and **10,106 records in 2018–2022** (annual counts: 2018 = 1,738; 2019 = 1,665; 2020 = 2,178; 2021 = 2,338; 2022 = 2,187). It also identified **six ambiguous exact matches** and **161 county-code-54 records**. The standalone pipeline **was run against both original source files on October 28, 2026**; all count checks passed and the generated CSV contained exactly 10,106 records. Six synthetic regression tests also passed. The files themselves are not checked into this repo.

## Interpretation and limitations

**Unit of analysis: source homicide victim records**, not proven unique people or homicide incidents. The project does not calculate population-adjusted rates or causal effects. Exact matches without case identifiers may represent separate people; reporting changes in 2021–2022 may complicate time comparisons. See the [California DOJ OpenJustice portal](https://openjustice.doj.ca.gov/data) for source context.

## Author

Ismael Soto Jr. — Master of Public Policy and Graduate Certificate in Applied Data Science, UC Berkeley.

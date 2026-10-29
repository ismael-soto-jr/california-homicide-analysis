# Data provenance and reproducibility

This project is built from a historical **August 2023 download** of the California DOJ Criminal Justice Statistics Center's homicide data, documented by the June 2023 *Homicide File Context* codebook. The current live OpenJustice portal may provide a more recent extract with a different schema or revised counts.

## Source access

- DOJ OpenJustice portal: https://openjustice.doj.ca.gov/data
- Historical homicide source expected by this specific script: `HomicideActuals1987-2022.csv`
- Separate agency/county crosswalk workbook: `NCIC Code Jurisdiction List_04242023.xlsx`
- The historical source documentation is summarized in [source_codebook.md](source_codebook.md).

**Do not assume the currently downloadable DOJ files reproduce our frozen 2018–2022 historical extract.** The original archived inputs were privately retained by the project author. They are not part of this public-intended repository because source versioning and redistribution permissions have not yet been independently confirmed.

## Two levels of reproducibility

1. **Open, no external data needed:** Install `requirements.txt`, run `python -m pytest -q`, `python examples/synthetic_demo.py`, and `python scripts/build_figures.py --from-summaries`. These exercises the pipeline on invented data and recreate the publication figures from the verified aggregate tables.
2. **Complete historical rebuild (requires archived source files):** Put the two input files under `data/raw/`, run `python prepare_homicides.py`, then `python scripts/build_figures.py`. The script asserts the historical row counts and stops on mismatches.

The synthetic demo is illustrative and is not a substitute for the separately completed real-data validation. The aggregate tables permit checking figures but cannot prove all the individual-level cleaning steps. This limitation will remain disclosed when the repository is public.

## Data interpretation

The file holds source **actual/willful homicide victim records** (crime status 1), not verified distinct incidents or population-adjusted rates. Its `incident_date` records the date of assault, which is not necessarily the date of death. DOJ warns that reporting changes during 2021–2022 complicate comparisons. See [research findings](../reports/exploratory_findings.md).

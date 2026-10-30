# Reconciliation with the California DOJ published homicide report (2018–2022)

## Why this check matters

The archived August 2023 DOJ OpenJustice CSV used for this project contains **10,106 actual/willful homicide victim-source rows** with assault years 2018–2022. California DOJ's separately published *Homicide in California 2022* report, Table 14, gives **10,187 homicide-crime/known-victim counts** summed over those years. The difference is **81**, but the reasons have not been established.

The report explicitly states that reported homicide crimes represent **known victims** (Understanding the Data, PDF page 7). Consequently, differences should not be dismissed as an obvious crime-versus-victim unit mismatch. Historical source version, revised agency submissions, incident/assault timing, and reporting formats require investigation before attributing causes.

## Independently checked publication reference

Source: California Department of Justice, Criminal Justice Statistics Center, [*Homicide in California 2022*](https://data-openjustice.doj.ca.gov/sites/default/files/2023-06/Homicide%20In%20CA%202022f.pdf), **Table 14, printed pp. 19–20 (PDF pp. 23–24)**, county-by-year **Number** panel.

The published [county-year Table 14 reference](../reports/doj_published_table14_county_year.csv) has **58 counties × 5 years = 290 rows**, including explicitly reported zeros. It was transcribed from the two table pages and independently checked so each year sums exactly to the report's statewide total.

| Assault year in archived CSV | Archived victim-source rows | Published Table 14 known-victim homicide crimes | Archived minus published |
| --- | ---: | ---: | ---: |
| 2018 | 1,738 | 1,739 | -1 |
| 2019 | 1,665 | 1,679 | -14 |
| 2020 | 2,178 | 2,202 | -24 |
| 2021 | 2,338 | 2,361 | -23 |
| 2022 | 2,187 | 2,206 | -19 |
| **Total** | **10,106** | **10,187** | **-81** |

**Amador example:** Archived CSV contains **3 source rows coded crime status 1 in 2019**, with **no exact duplicate entire rows**, and **0 coded rows for 2020**. Table 14 publishes **1** and **2**, respectively. These are diagnostic differences, not proof that any source records are wrong or should be deleted/added. The published table lists **0** for Amador in 2022.

## Run the comparison locally

Without original archived data, check only the published 290-row table:

```bash
python scripts/reconcile_doj_publication.py --check-reference
```

With the **full historical cleaned data** already built by `prepare_homicides.py`:

```bash
python scripts/reconcile_doj_publication.py
```

This creates a **Git-ignored local output**:

`data/processed/doj_county_reconciliation_2018_2022.csv`

The script reports annual differences and the largest county-year discrepancies. It also distinguishes **no rows in the archived extract** from **published zero occurrences**. The reference table contains published zeros; it is not appropriate to impute all absent archived records as actual zeros or treat the published data as if they were source records.

## Analytical boundaries

- A clean local data pipeline and exact expected historical totals establish **internal consistency**, not agreement with the separately published DOJ series.
- The archived file and official report may represent different data snapshots/revisions; reasons for discrepancies require independent corroboration.
- DOJ began combining SRS and incident-based reporting in 2021–2022. Direct cross-year comparability requires caution.
- The **county of the reporting agency** in the archived extract is not necessarily the county of residence of each victim.
- The population workbook prepared for the exploratory extension uses separately published **E-2 denominators**, which can have different benchmarks than the population values embedded in the 2022 DOJ report.
- Do not overwrite archived source rows with published counts, conflate a cross-source difference with a processing error, or publish definitive county rankings before assessing coverage and revision issues.

## Reproduction and audit

The published county-year table has exact key uniqueness, nonnegative integers, **290 rows**, and per-year statewide sum checks in the Python reconciliation script. Additional synthetic tests exercise positive/negative discrepancies, unmatched county-year keys, duplicate references, and absent source rows. GitHub Actions can verify the **published reference** without the historical individual-level CSV.

These checks, the original population join, and the separate descriptive figures are intentionally distinct stages.

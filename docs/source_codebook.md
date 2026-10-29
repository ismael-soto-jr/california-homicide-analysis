# Source data dictionary and interpretation notes

**Primary reference:** California Department of Justice, Criminal Justice Statistics Center (CJSC), *Homicide File Context*, revised June 2023, 12 pages (historical copy supplied for this project: `Homicide Context_2018_2022_06122023 .pdf`). See also the [California DOJ OpenJustice data portal](https://openjustice.doj.ca.gov/data). Page references below refer to the June 2023 document.

This document records field definitions relevant to the preparation script. It **does not replace** the full DOJ codebook, and it does not claim that current-year files use identical conventions.

## Analytical scope and unit

- The source holds records describing **homicide victims** and circumstances reported by participating California law enforcement agencies (p. 1).
- **Crime status:** `Crm Stat` = `1` is **Actual/Willful Homicide**. Other codes are `2` Citizen Justifiable, `3` Manslaughter, and `4` Peace Officer Justifiable (p. 5). In the historical 2018–2022 extract, **all 10,106 selected rows have crime-status code 1**, verified against the source CSV. The preparation script now fails if any selected row has another status.
- A source **victim record** is not necessarily a distinct **incident**. Do not treat the number of records as verified unique victims or use it as a rate without population denominators.
- In 2021–2022, the source combines summary reporting and incident-based reporting. DOJ cautions against unqualified comparisons with earlier years (pp. 1–2).
- Incident month/day/year describe **the assault that ultimately caused death**, not necessarily the date of death (p. 6). Thus our derived `incident_date` is the *assault date*.

## Source columns and coding

| Source field | Derived field | Interpretation |
| --- | --- | --- |
| `CO` | `county_code`, `county` | 2-digit county identifier for reporting agency (p. 4); joined with separately validated NCIC lookup |
| `Inc YR`, `Inc MO`, `Inc day` | `incident_year`, `incident_month`, `incident_date` | Date of assault ultimately resulting in death (p. 6) |
| `Crm Stat` | Validation only | Code 1 = Actual/Willful Homicide (p. 5) |
| `V age` | `victim_age_code`, `victim_age_group` | Age code: `00` unknown, `01–98` corresponding age, `99` 99+, `NB` birth–one week, `BB` one week–12 months (p. 5) |
| `V sex` | `victim_sex_code` | `0` unknown; `1` male; `2` female; blank not reported (pp. 4–5) |
| `V race` | `victim_race_code` | **Combined race/ethnicity** code, not two independent fields (pp. 4–5) |

### Race/ethnicity codes

The DOJ's source codebook (p. 5) defines these codes:

| Code | Meaning | Code | Meaning |
| --- | --- | --- | --- |
| `0`, `X` | Unknown | `W`, `1` | White |
| `H`, `2` | Hispanic | `B`, `3` | Black |
| `I`, `4` | American Indian | `C`, `5` | Chinese |
| `J`, `6` | Japanese | `F`, `7` | Filipino |
| `O`, `8` | Other | `P`, `9` | Pacific Islander |
| `A` | Other Asian | `D` | Cambodian |
| `G` | Guamanian | `K` | Korean |
| `L` | Laotian | `S` | Samoan |
| `U` | Hawaiian | `V` | Vietnamese |
| `Z` | Asian Indian | | |

The source mixes race and Hispanic ethnicity categories. It should not be merged directly with independently defined Census race and ethnicity groups without an explicit, documented concordance. Agency-specific reporting limitations also apply (pp. 3–4).

### Important sex/gender reporting note

The DOJ notes that newer California incident-based reporting includes categories beyond male and female. However, two non-binary individuals included in the 2022 homicide publication were **excluded from the downloadable homicide data file** due to the small population size (p. 2). A description of the file must therefore avoid claiming it includes every published record or every sex/gender category.

## Fields not yet included

The source also contains **means of death/weapon**, **location of assault**, **victim–offender relationship**, and **precipitating event** fields (pp. 6–9). Their documented codes can support later research questions, but they are deliberately not in the initial concise pipeline. They should be audited before any additional recoding or graphics.

## Methodology and design choices

- The revised pipeline retains six exact matching source rows with missing case identifiers rather than assuming they are duplicated victims.
- A validated many-to-one county lookup prevents the NCIC code 54 (Tulare) mislabel from multiplying records.
- The current analysis is descriptive. Year comparisons reflect recorded victim *rows*, not causal effects, rates, or independent unique incidents.
- Data source is a fixed historical extract downloaded August 2023; do not present it as current homicide surveillance.

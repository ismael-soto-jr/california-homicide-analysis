"""Demonstrate real preparation logic on invented records; no DOJ source files needed.

Run: python examples/synthetic_demo.py
"""
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_homicides import prepare

# These invented observations are demonstrations, NOT real homicide data.
source = pd.DataFrame({
    "Inc YR": [2017, 2018, 2022, 2022],
    "Inc MO": [1, 6, 3, 3],
    "Inc day": [4, 12, 5, 5],
    "CO": [16, 54, 1, 1],
    "V age": ["0", "NB", "30", "30"],
    "V sex": [0, 2, 1, 1],
    "V race": ["X", "H", "W", "W"],
    "Crm Stat": [1, 1, 1, 1],
})

# A deliberately defective reference lookup: county code 54 includes an
# erroneous Kings County row. The pipeline removes only this known conflict.
reference = pd.DataFrame({
    "CntyCode": [1, 16, 54, 54],
    "County": ["Alameda County", "Kings County", "Tulare County", "Kings County"],
})
prepared = prepare(source, reference)
assert len(prepared) == 3
assert prepared["county"].tolist() == [
    "Tulare County", "Alameda County", "Alameda County"
]
assert prepared["source_csv_row"].tolist() == [3, 4, 5]
print("Synthetic preparation demonstration: 3 source rows preserved.")
print(prepared[["incident_year", "county", "victim_age_group"]].to_string(index=False))

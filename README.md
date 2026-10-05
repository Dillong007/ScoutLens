# Parallel XI

**A position-aware Premier League player-similarity application.**

Parallel XI identifies statistically comparable players and explains each match through per-90 metrics, position-relative percentiles, and interactive visualizations.

[Open the live application](https://parallel-xi-analytics.streamlit.app)

## Overview

Player comparisons are most useful when they reflect positional responsibilities. Parallel XI therefore evaluates forwards, midfielders, and defenders with different eight-metric profiles rather than applying one universal definition of similarity.

Users can:

- Search 300 eligible Premier League outfield players
- Discover five statistically similar same-position players
- Compare position-relative percentile profiles on an interactive radar chart
- Review exact per-90 values and standardized metric gaps
- Inspect the methodology, data source, validation, and limitations

## Methodology

The project transforms player-match records into season-level profiles:

1. Combine all 38 gameweeks of 2025/26 Premier League data.
2. Remove player-match records with zero minutes played.
3. Aggregate match statistics into season totals.
4. Convert profile metrics into per-90 rates.
5. Retain outfield players with at least 900 minutes and at least 80% detailed-metric coverage.
6. Assign separate feature sets to forwards, midfielders, and defenders.
7. Standardize each metric within its positional group using `StandardScaler`.
8. Calculate Euclidean distance between same-position player profiles.
9. Return the five players with the smallest profile distances.

A smaller profile distance represents greater statistical similarity. Radar-chart values are percentiles relative to other eligible players in the same positional group.

## Position-Specific Features

| Forwards | Midfielders | Defenders |
|---|---|---|
| Shots | Expected goals | Tackles won |
| Expected goals | Expected assists | Interceptions |
| Expected assists | Chances created | Recoveries |
| Chances created | Opposition-box touches | Blocks |
| Opposition-box touches | Final-third passes | Clearances |
| Successful dribbles | Accurate passes | Aerial duels won |
| Final-third passes | Successful dribbles | Accurate passes |
| Aerial duels won | Recoveries | Final-third passes |

The machine-readable configuration is stored in `data/processed/position_features.json`.

## Data

The project uses public 2025/26 Premier League player-match data from the [FPL Core Insights repository](https://github.com/olbauday/FPL-Core-Insights).

The raw source contains:

- 12,754 player-match records
- 380 matches
- 565 players

After the playing-time and coverage requirements are applied, the comparison pool contains 300 players:

- 146 midfielders
- 125 defenders
- 29 forwards

The processed player profiles are included so the application can run without downloading the raw datasets.

## Project Structure

```text
parallel-xi-football-analytics/
├── .streamlit/
│   └── config.toml
├── data/
│   ├── raw/                         # Recreated by the loading script
│   └── processed/
│       ├── parallel_xi_position_profiles.csv
│       └── position_features.json
├── docs/
│   └── model_validation.md
├── src/
│   ├── 01_load_data.py
│   ├── 02_build_profiles.py
│   └── 03_similarity.py
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Run Locally

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python src/01_load_data.py
python src/02_build_profiles.py
python src/03_similarity.py
python -m streamlit run app.py
```

Because the processed profiles are included, the application can also be launched immediately after installing the requirements:

```bash
python -m streamlit run app.py
```

## Validation

The recommendations were manually reviewed for ten recognizable players spanning strikers, wide attackers, central midfielders, centre-backs, and fullbacks. All ten produced positionally and stylistically plausible comparison sets.

This face-validity review does not prove predictive performance, but it provides a practical check that the position-specific features and distance calculations behave as intended. Full results are documented in [`docs/model_validation.md`](docs/model_validation.md).

## Limitations

- Similarity does not measure overall player quality.
- Results describe the 2025/26 season and do not predict future performance or transfer success.
- Broad positional labels do not capture every tactical role.
- Per-90 statistics remain influenced by team style, possession, and opposition strength.
- Age, injuries, league context, and transfer value are not modeled.
- Recommendations should support scouting judgment rather than replace video analysis.

## Technology

- Python
- pandas
- scikit-learn
- Plotly
- Streamlit

## Attribution

This is an independent educational portfolio project. It is not affiliated with the Premier League, FPL Core Insights, or any professional club or commercial scouting platform. Source data remains subject to the rights and terms of its respective providers.

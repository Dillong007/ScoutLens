# ScoutLens

ScoutLens is an interactive Premier League player-similarity application that identifies statistically comparable players using position-aware performance profiles.

Rather than evaluating every player through the same universal metrics, ScoutLens uses different feature sets for forwards, midfielders, and defenders to better reflect their positional responsibilities.

## Features

- Search 300 eligible Premier League players
- Discover the five most statistically similar players
- Compare only players within the same positional group
- Explore position-relative percentile radar charts
- Review exact per-90 values and standardized differences
- Reproduce the analysis from the original raw data
- Access documented model-validation results

## Methodology

ScoutLens transforms player-match records into season-level profiles through the following process:

1. Combine all 38 gameweeks of 2025/26 Premier League data.
2. Remove player-match records with zero minutes played.
3. Aggregate match statistics into season totals.
4. Convert performance metrics into per-90 rates.
5. Require at least 900 minutes and sufficient data coverage.
6. Assign position-specific feature sets to forwards, midfielders, and defenders.
7. Standardize features within each positional group using `StandardScaler`.
8. Calculate Euclidean distance between player profiles.
9. Rank each player’s five closest same-position matches.

A smaller profile distance indicates greater statistical similarity.

Radar-chart values represent a player’s percentile relative to other eligible players in the same positional group.

## Position-Aware Modeling

ScoutLens selects eight metrics for each positional group from performance areas including:

- Shooting and expected goals
- Chance creation and expected assists
- Penalty-area involvement
- Progressive and final-third passing
- Dribbling
- Recoveries and defensive actions
- Aerial involvement
- Ball distribution

The exact feature configuration is stored in:

```text
data/processed/position_features.json
```

This approach prevents defenders, midfielders, and forwards from being evaluated through identical expectations.

## Project Structure

```text
ScoutLens/
├── .streamlit/
│   └── config.toml
├── data/
│   ├── raw/
│   └── processed/
│       ├── scoutlens_position_profiles.csv
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

## Running ScoutLens Locally

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Install the required packages

```bash
python -m pip install -r requirements.txt
```

### 3. Download the raw datasets

```bash
python src/01_load_data.py
```

### 4. Build the position-aware player profiles

```bash
python src/02_build_profiles.py
```

### 5. Run the model-validation script

```bash
python src/03_similarity.py
```

### 6. Launch the application

```bash
python -m streamlit run app.py
```

Because the processed profiles are included with the project, the Streamlit application can also be launched immediately after installing the required packages.

## Model Validation

The similarity model was reviewed using recognizable examples across all three positional groups.

The validation set included players such as:

- Bukayo Saka
- Erling Haaland
- Mohamed Salah
- Declan Rice
- Virgil van Dijk
- Adrien Truffert
- Ollie Watkins
- Ibrahima Konaté

The results produced positionally and stylistically plausible recommendations across the tested profiles.

Additional findings are documented in:

```text
docs/model_validation.md
```

## Data

The project uses public 2025/26 Premier League player-match data obtained from the [FPL Core Insights repository](https://github.com/olbauday/FPL-Core-Insights).

The raw datasets contain:

- 12,754 player-match records
- 380 unique matches
- 565 unique players

After the playing-time and data-coverage requirements are applied, ScoutLens contains 300 eligible player profiles:

- 146 midfielders
- 125 defenders
- 29 forwards

## Limitations

- Broad positional labels cannot distinguish every tactical role.
- Statistical similarity does not necessarily represent equal player quality.
- Team tactics, opposition strength, injuries, age, and transfer value are not modeled.
- Per-90 statistics can still be influenced by role, possession, and team context.
- The application depends on the accuracy and continued availability of the public source data.

ScoutLens should therefore be interpreted as an exploratory scouting and player-comparison tool rather than a complete recruitment model.

## Technology

- Python
- pandas
- scikit-learn
- Plotly
- Streamlit
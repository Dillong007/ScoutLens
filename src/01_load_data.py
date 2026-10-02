import pandas as pd
from pathlib import Path


# Locate the project folders
project_folder = Path(__file__).resolve().parent.parent
raw_folder = project_folder / "data" / "raw"

raw_folder.mkdir(
    parents=True,
    exist_ok=True,
)


# GitHub location containing the match data
base_url = (
    "https://raw.githubusercontent.com/"
    "olbauday/FPL-Core-Insights/main/"
    "data/2025-2026/By%20Tournament/"
    "Premier%20League"
)


# Download all 38 gameweeks
gameweek_tables = []

for gameweek in range(1, 39):
    file_url = (
        f"{base_url}/GW{gameweek}/"
        "playermatchstats.csv"
    )

    gameweek_data = pd.read_csv(
        file_url,
        low_memory=False,
    )

    gameweek_data["gameweek"] = gameweek
    gameweek_tables.append(gameweek_data)

    print(
        f"Loaded GW{gameweek}: "
        f"{len(gameweek_data)} rows"
    )


# Combine all gameweeks
player_matches = pd.concat(
    gameweek_tables,
    ignore_index=True,
)


# Check the combined data
duplicate_count = player_matches.duplicated(
    subset=["player_id", "match_id"]
).sum()

if duplicate_count > 0:
    raise ValueError(
        f"Found {duplicate_count} duplicate "
        "player-match rows."
    )


# Download player and team metadata
players_url = (
    "https://raw.githubusercontent.com/"
    "olbauday/FPL-Core-Insights/main/"
    "data/2025-2026/players.csv"
)

teams_url = (
    "https://raw.githubusercontent.com/"
    "olbauday/FPL-Core-Insights/main/"
    "data/2025-2026/teams.csv"
)

players = pd.read_csv(players_url)
teams = pd.read_csv(teams_url)


# Save the raw datasets
player_matches.to_csv(
    raw_folder
    / "premier_league_2025_26_player_matches.csv",
    index=False,
)

players.to_csv(
    raw_folder
    / "premier_league_2025_26_players.csv",
    index=False,
)

teams.to_csv(
    raw_folder
    / "premier_league_2025_26_teams.csv",
    index=False,
)


print("\nData download complete.")

print(
    f"Player-match data: {player_matches.shape}"
)

print(
    f"Unique matches: "
    f"{player_matches['match_id'].nunique()}"
)

print(
    f"Unique players: "
    f"{player_matches['player_id'].nunique()}"
)

print(f"Player metadata: {players.shape}")
print(f"Team metadata: {teams.shape}")

print(
    f"\nRaw datasets saved to:\n{raw_folder}"
)
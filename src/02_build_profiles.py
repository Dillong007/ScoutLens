import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import json
# Locate the ScoutLens project folder
project_folder = Path(__file__).resolve().parents[1]
data_folder = project_folder / "data/raw"


# Load the raw datasets
player_matches = pd.read_csv(
    data_folder
    / "premier_league_2025_26_player_matches.csv"
)

players = pd.read_csv(
    data_folder
    / "premier_league_2025_26_players.csv"
)

teams = pd.read_csv(
    data_folder
    / "premier_league_2025_26_teams.csv"
)


# Metrics being considered for position-aware profiles
candidate_metrics = [
    "total_shots",
    "xg",
    "xa",
    "chances_created",
    "touches_opposition_box",
    "final_third_passes",
    "successful_dribbles",
    "recoveries",
    "accurate_passes",
    "tackles_won",
    "interceptions",
    "blocks",
    "clearances",
    "aerial_duels_won",
    "accurate_crosses",
    "duels_won",
]


# Confirm every proposed metric exists
missing_columns = [
    metric
    for metric in candidate_metrics
    if metric not in player_matches.columns
]

if missing_columns:
    raise ValueError(
        f"Missing candidate metrics: {missing_columns}"
    )


# Inspect metric quality before selecting the final features
metric_audit = pd.DataFrame(
    {
        "data_type": player_matches[
            candidate_metrics
        ].dtypes.astype(str),

        "missing_percent": (
            player_matches[candidate_metrics]
            .isna()
            .mean()
            .mul(100)
            .round(2)
        ),

        "zero_percent": (
            player_matches[candidate_metrics]
            .eq(0)
            .mean()
            .mul(100)
            .round(2)
        ),
    }
)


print("Player-match data:", player_matches.shape)
print("Player metadata:", players.shape)
print("Team metadata:", teams.shape)

print("\nPosition-metric audit:")
print(metric_audit)

# Keep only players who entered the match
audit_data = player_matches[
    player_matches["minutes_played"] > 0
].copy()


# Add each player's position
audit_data = audit_data.merge(
    players[
        [
            "player_id",
            "position",
        ]
    ],
    on="player_id",
    how="left",
    validate="many_to_one",
)


# Goalkeepers are outside the current Parallel XI model
audit_data = audit_data[
    audit_data["position"] != "Goalkeeper"
]


# Compare metric sparsity within each position
zero_percent_by_position = (
    audit_data
    .groupby("position")[candidate_metrics]
    .agg(
        lambda metric:
        metric.eq(0).mean() * 100
    )
    .round(1)
    .transpose()
)


print("\nZero percentages by position:")
print(zero_percent_by_position)

position_features = {
    "Forward": [
        "total_shots",
        "xg",
        "xa",
        "chances_created",
        "touches_opposition_box",
        "successful_dribbles",
        "final_third_passes",
        "aerial_duels_won",
    ],

    "Midfielder": [
        "xg",
        "xa",
        "chances_created",
        "touches_opposition_box",
        "final_third_passes",
        "accurate_passes",
        "successful_dribbles",
        "recoveries",
    ],

    "Defender": [
        "tackles_won",
        "interceptions",
        "recoveries",
        "blocks",
        "clearances",
        "aerial_duels_won",
        "accurate_passes",
        "final_third_passes",
    ],
}


# Create one list containing every metric needed
all_profile_metrics = sorted(
    {
        metric
        for metrics in position_features.values()
        for metric in metrics
    }
)


print("\nMetrics needed for the position-aware model:")
print(all_profile_metrics)
# Create readable player names
players["full_name"] = (
    players["first_name"].fillna("").str.strip()
    + " "
    + players["second_name"].fillna("").str.strip()
).str.strip()

players["full_name"] = players["full_name"].where(
    players["full_name"] != "",
    players["web_name"],
)


# Add player metadata
player_lookup = players[
    [
        "player_id",
        "web_name",
        "full_name",
        "position",
        "team_code",
    ]
]

scout_data = player_matches.merge(
    player_lookup,
    on="player_id",
    how="left",
    validate="many_to_one",
)


# Add team names
team_lookup = teams[
    [
        "code",
        "name",
    ]
].rename(
    columns={
        "code": "team_code",
        "name": "team_name",
    }
)

scout_data = scout_data.merge(
    team_lookup,
    on="team_code",
    how="left",
    validate="many_to_one",
)


# Remove records where the player did not enter the match
played_data = scout_data[
    scout_data["minutes_played"] > 0
].copy()


# These metrics share incomplete match coverage
detail_metrics = [
    "touches_opposition_box",
    "final_third_passes",
    "blocks",
]

reference_missing_rows = played_data[
    detail_metrics[0]
].isna()

for metric in detail_metrics[1:]:
    if not reference_missing_rows.equals(
        played_data[metric].isna()
    ):
        raise ValueError(
            f"{metric} has a different missing-data pattern."
        )


# Record minutes where detailed metrics were available
played_data["detail_metric_minutes"] = (
    played_data["minutes_played"].where(
        ~reference_missing_rows,
        0,
    )
)


print(
    "\nPlayable player-match rows:",
    len(played_data),
)

print(
    "Missing player names:",
    played_data["full_name"].isna().sum(),
)

print(
    "Missing team names:",
    played_data["team_name"].isna().sum(),
)

print(
    "Detailed-data rows missing:",
    reference_missing_rows.sum(),
)
# Define how each player should be summarized
aggregation_rules = {
    "matches_played": (
        "match_id",
        "nunique",
    ),
    "minutes_played": (
        "minutes_played",
        "sum",
    ),
    "detail_metric_minutes": (
        "detail_metric_minutes",
        "sum",
    ),
}

for metric in all_profile_metrics:
    aggregation_rules[metric] = (
        metric,
        "sum",
    )


# Create one season-level row per player
player_summary = (
    played_data
    .groupby(
        [
            "player_id",
            "web_name",
            "full_name",
            "position",
            "team_name",
        ],
        as_index=False,
    )
    .agg(**aggregation_rules)
)


# Convert every profile metric into a per-90 rate
for metric in all_profile_metrics:
    if metric in detail_metrics:
        denominator_column = "detail_metric_minutes"
    else:
        denominator_column = "minutes_played"

    denominator = player_summary[
        denominator_column
    ].where(
        player_summary[denominator_column] > 0
    )

    player_summary[f"{metric}_per90"] = (
        player_summary[metric]
        / denominator
        * 90
    )


# Calculate detailed-data coverage
player_summary["detail_data_coverage"] = (
    player_summary["detail_metric_minutes"]
    / player_summary["minutes_played"]
)


# Establish the eligible comparison pool
minimum_minutes = 900

eligible_players = player_summary[
    (player_summary["position"] != "Goalkeeper")
    & (
        player_summary["minutes_played"]
        >= minimum_minutes
    )
    & (
        player_summary["detail_data_coverage"]
        >= 0.80
    )
].copy()


print(
    "\nSeason player profiles:",
    len(player_summary),
)

print(
    "Eligible position-aware profiles:",
    len(eligible_players),
)

print("\nEligible players by position:")
print(
    eligible_players["position"]
    .value_counts()
)
# Prepare columns for position-specific scores
for metric in all_profile_metrics:
    eligible_players[
        f"scaled_{metric}_per90"
    ] = float("nan")

    eligible_players[
        f"{metric}_percentile"
    ] = float("nan")


# Scale and rank players only against their position
for position, metrics in position_features.items():
    position_mask = (
        eligible_players["position"] == position
    )

    per90_columns = [
        f"{metric}_per90"
        for metric in metrics
    ]

    scaled_columns = [
        f"scaled_{metric}_per90"
        for metric in metrics
    ]

    scaler = StandardScaler()

    eligible_players.loc[
        position_mask,
        scaled_columns,
    ] = scaler.fit_transform(
        eligible_players.loc[
            position_mask,
            per90_columns,
        ]
    )

    for metric in metrics:
        per90_column = f"{metric}_per90"
        percentile_column = f"{metric}_percentile"

        eligible_players.loc[
            position_mask,
            percentile_column,
        ] = (
            eligible_players.loc[
                position_mask,
                per90_column,
            ]
            .rank(pct=True)
            .mul(100)
        )


# Save separately so the working MVP remains untouched
processed_folder = (
    project_folder
    / "data/processed"
)

processed_folder.mkdir(
    parents=True,
    exist_ok=True,
)

position_profiles_file = (
    processed_folder
    / "parallel_xi_position_profiles.csv"
)

eligible_players.to_csv(
    position_profiles_file,
    index=False,
)


print(
    "\nPosition-aware profiles saved:",
    position_profiles_file,
)

print(
    "Saved profile shape:",
    eligible_players.shape,
)

position_features_file = (
    processed_folder
    / "position_features.json"
)

with open(
    position_features_file,
    "w",
    encoding="utf-8",
) as configuration_file:
    json.dump(
        position_features,
        configuration_file,
        indent=2,
    )

print(
    "Position-feature configuration saved:",
    position_features_file,
)
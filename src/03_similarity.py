import json
import pandas as pd
from pathlib import Path
from sklearn.metrics import pairwise_distances


project_folder = Path(__file__).resolve().parents[1]
processed_folder = project_folder / "data/processed"


# Load position-aware profiles
profiles = pd.read_csv(
    processed_folder
    / "parallel_xi_position_profiles.csv"
)


# Load the position-specific metric definitions
with open(
    processed_folder
    / "position_features.json",
    "r",
    encoding="utf-8",
) as configuration_file:
    position_features = json.load(
        configuration_file
    )


def find_similar_players(
    player_id,
    number_of_results=5,
):
    selected_player = profiles[
        profiles["player_id"] == player_id
    ]

    if selected_player.empty:
        raise ValueError(
            f"Player ID {player_id} is not eligible."
        )

    selected_position = selected_player[
        "position"
    ].iloc[0]

    metrics = position_features[
        selected_position
    ]

    scaled_columns = [
        f"scaled_{metric}_per90"
        for metric in metrics
    ]

    candidates = profiles[
        (
            profiles["position"]
            == selected_position
        )
        & (
            profiles["player_id"]
            != player_id
        )
    ].copy()

    candidates["profile_distance"] = (
        pairwise_distances(
            candidates[scaled_columns],
            selected_player[scaled_columns],
            metric="euclidean",
        ).ravel()
    )

    results = (
        candidates
        .sort_values("profile_distance")
        .head(number_of_results)
    )

    return results[
        [
            "player_id",
            "full_name",
            "team_name",
            "position",
            "minutes_played",
            "profile_distance",
        ]
    ]


def find_player_id(full_name):
    matches = profiles[
        profiles["full_name"].str.casefold()
        == full_name.casefold()
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Found {len(matches)} players named "
            f"'{full_name}'."
        )

    return int(
        matches["player_id"].iloc[0]
    )


validation_players = [
    "Bukayo Saka",
    "Erling Haaland",
    "Virgil van Dijk",
    "Adrien Truffert",
    "Declan Rice",
    "Mohamed Salah",
    "Ollie Watkins",
    "Ibrahima Konaté",
    "Dominik Szoboszlai",
    "Ola Aina",
]


for player_name in validation_players:
    player_id = find_player_id(
        player_name
    )

    results = find_similar_players(
        player_id=player_id,
        number_of_results=5,
    )

    print(
        f"\nPosition-aware matches for "
        f"{player_name}:"
    )

    print(
        results
        .round(2)
        .to_string(index=False)
    )

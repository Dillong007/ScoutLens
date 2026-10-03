import pandas as pd
import streamlit as st
from pathlib import Path
from sklearn.metrics import pairwise_distances
import plotly.graph_objects as go
import json
st.set_page_config(
    page_title="Parallel XI",
    page_icon="⚽",
    layout="wide",
)

project_folder = Path(__file__).resolve().parent
processed_folder = project_folder / "data/processed"

@st.cache_data
def load_profiles():
    return pd.read_csv(
        processed_folder
        / "parallel_xi_position_profiles.csv"
    )

@st.cache_data
def load_position_features():
    with open(
        processed_folder
        / "position_features.json",
        "r",
        encoding="utf-8",
    ) as configuration_file:
        return json.load(
            configuration_file
        )


profiles = load_profiles()

position_features = (
    load_position_features()
)


st.title("⚽ Parallel XI")

st.write(
    "Compare Premier League players across eight "
    "position-specific performance dimensions and "
    "discover statistically similar alternatives."
)

# Create readable player labels
player_labels = {
    row["player_id"]: (
        f"{row['full_name']} — "
        f"{row['team_name']} "
        f"({row['position']})"
    )
    for _, row in profiles.iterrows()
}

selected_player_id = st.selectbox(
    "Select a player",
    options=sorted(
        profiles["player_id"].tolist(),
        key=lambda player_id: player_labels[player_id],
    ),
    format_func=lambda player_id: player_labels[player_id],
)

selected_player = profiles[
    profiles["player_id"] == selected_player_id
]

selected_position = selected_player[
    "position"
].iloc[0]
selected_metrics = position_features[
    selected_position
]

scaled_columns = [
    f"scaled_{metric}_per90"
    for metric in selected_metrics
]
selected_player_row = selected_player.iloc[0]
st.subheader(
    f"{selected_player_row['full_name']} Profile"
)

team_column, position_column, minutes_column, matches_column = (
    st.columns(4)
)

team_column.metric(
    "Team",
    selected_player_row["team_name"],
)

position_column.metric(
    "Position",
    selected_player_row["position"],
)

minutes_column.metric(
    "Minutes",
    f"{int(selected_player_row['minutes_played']):,}",
)

matches_column.metric(
    "Matches",
    int(selected_player_row["matches_played"]),
)
# Compare the player with others in the same position
candidates = profiles[
    (profiles["position"] == selected_position)
    & (profiles["player_id"] != selected_player_id)
].copy()
if candidates.empty:
    st.warning(
        "No eligible same-position comparison "
        "players are available."
    )
    st.stop()
candidates["profile_distance"] = (
    pairwise_distances(
        candidates[scaled_columns],
        selected_player[scaled_columns],
        metric="euclidean",
    ).ravel()
)
similar_players = (
    candidates
    .sort_values("profile_distance")
    .head(5)
)

st.subheader("Most Similar Players")
st.caption(
    "Lower profile distance indicates a closer "
    "statistical match within the same position."
)
display_table = similar_players[
    [
        "full_name",
        "team_name",
        "position",
        "minutes_played",
        "profile_distance",
    ]
].copy()

display_table["profile_distance"] = (
    display_table["profile_distance"].round(2)
)

display_table = display_table.rename(
    columns={
        "full_name": "Player",
        "team_name": "Team",
        "position": "Position",
        "minutes_played": "Minutes",
        "profile_distance": "Profile Distance",
    }
)

display_table["Minutes"] = (
    display_table["Minutes"]
    .map(lambda minutes: f"{int(minutes):,}")
)

display_table["Profile Distance"] = (
    display_table["Profile Distance"]
    .map(lambda distance: f"{distance:.2f}")
)

st.dataframe(
    display_table,
    hide_index=True,
    width="stretch",
)
# Select one of the recommended players for comparison
st.subheader("Head-to-Head Comparison")
comparison_player_id = st.selectbox(
    "Choose one recommended player",
    options=similar_players["player_id"].tolist(),
    format_func=lambda player_id: player_labels[player_id],
)

comparison_player = profiles[
    profiles["player_id"] == comparison_player_id
].iloc[0]

# Radar-chart configuration
# Readable names for every possible metric
metric_display_names = {
    "total_shots": "Shots",
    "xg": "Expected Goals",
    "xa": "Expected Assists",
    "chances_created": "Chances Created",
    "touches_opposition_box": "Box Touches",
    "final_third_passes": "Final-Third Passes",
    "successful_dribbles": "Successful Dribbles",
    "recoveries": "Recoveries",
    "accurate_passes": "Accurate Passes",
    "tackles_won": "Tackles Won",
    "interceptions": "Interceptions",
    "blocks": "Blocks",
    "clearances": "Clearances",
    "aerial_duels_won": "Aerial Duels Won",
}

# Use labels and percentiles for the selected position
metric_labels = [
    metric_display_names[metric]
    for metric in selected_metrics
]

percentile_columns = [
    f"{metric}_percentile"
    for metric in selected_metrics
]

selected_values = (
    selected_player_row[percentile_columns]
    .astype(float)
    .tolist()
)

comparison_values = (
    comparison_player[percentile_columns]
    .astype(float)
    .tolist()
)

# Close each radar-chart shape
radar_labels = metric_labels + [metric_labels[0]]

selected_radar_values = (
    selected_values + [selected_values[0]]
)

comparison_radar_values = (
    comparison_values + [comparison_values[0]]
)

radar_chart = go.Figure()

radar_chart.add_trace(
    go.Scatterpolar(
        r=selected_radar_values,
        theta=radar_labels,
        fill="toself",
        fillcolor="rgba(49, 90, 71, 0.22)",
        line={
            "color": "#315A47",
            "width": 4,
        },
        marker={
            "color": "#315A47",
            "size": 7,
        },
        name=selected_player_row["full_name"],
    )
)

radar_chart.add_trace(
    go.Scatterpolar(
        r=comparison_radar_values,
        theta=radar_labels,
        fill="toself",
        fillcolor="rgba(196, 131, 62, 0.20)",
        line={
            "color": "#C4833E",
            "width": 4,
        },
        marker={
            "color": "#C4833E",
            "size": 7,
        },
        name=comparison_player["full_name"],
    )
)

radar_chart.update_layout(
    title="Position-Relative Player Profiles",
    template="plotly_white",
    paper_bgcolor="#F4F2ED",
    plot_bgcolor="#F4F2ED",
    font={
        "color": "#1B2420",
        "size": 13,
    },
    polar={
        "bgcolor": "#FCFBF8",
        "radialaxis": {
            "visible": True,
            "range": [0, 100],
            "gridcolor": "#D3D9D3",
            "linecolor": "#9CAA9F",
            "tickfont": {
                "color": "#56625C",
            },
        },
        "angularaxis": {
            "gridcolor": "#DFE4DF",
            "linecolor": "#9CAA9F",
            "tickfont": {
                "color": "#1B2420",
                "size": 13,
            },
        },
    },
    legend={
        "orientation": "h",
        "x": 0.5,
        "xanchor": "center",
        "y": -0.15,
    },
    margin={
        "l": 80,
        "r": 80,
        "t": 80,
        "b": 90,
    },
)


st.plotly_chart(
    radar_chart,
    width="stretch",
)
# Exact metric-by-metric comparison
per90_columns = [
    f"{metric}_per90"
    for metric in selected_metrics
]


comparison_scaled_columns = [
    f"scaled_{column}"
    for column in per90_columns
]

selected_name = selected_player_row["full_name"]
comparison_name = comparison_player["full_name"]

comparison_table = pd.DataFrame(
    {
        "Metric": metric_labels,
        f"{selected_name} per 90": [
            selected_player_row[column]
            for column in per90_columns
        ],
        f"{comparison_name} per 90": [
            comparison_player[column]
            for column in per90_columns
        ],
        f"{selected_name} percentile": [
            selected_player_row[column]
            for column in percentile_columns
        ],
        f"{comparison_name} percentile": [
            comparison_player[column]
            for column in percentile_columns
        ],
        "Standardized Gap": [
            abs(
                selected_player_row[column]
                - comparison_player[column]
            )
            for column in comparison_scaled_columns
        ],
    }
)

# Smaller gaps represent stronger similarities
comparison_table = comparison_table.sort_values(
    "Standardized Gap"
)

numeric_columns = comparison_table.columns[1:]

comparison_table[numeric_columns] = (
    comparison_table[numeric_columns].round(2)
)


closest_dimensions = (
    comparison_table["Metric"]
    .head(3)
    .tolist()
)


st.subheader("Why These Players Match")

st.write(
    "**Closest profile dimensions:** "
    + ", ".join(closest_dimensions)
    + "."
)

st.caption(
    "A smaller standardized gap means the players are "
    "more similar in that performance dimension."
)

st.dataframe(
    comparison_table,
    hide_index=True,
    width="stretch",
)

st.divider()

with st.expander(
    "Methodology, Data Source, and Limitations"
):
    st.markdown(
        """
### Data

Parallel XI uses 2025/26 Premier League player-match
data from the
[FPL Core Insights repository](https://github.com/olbauday/FPL-Core-Insights).

Only outfield players with at least 900 minutes and
at least 80% coverage for detailed metrics are included.

### Method

- Match statistics are aggregated into season totals.
- Metrics are converted into per-90-minute rates.
- Forwards, midfielders, and defenders use different
  eight-metric profiles.
- Metrics are standardized within each position.
- Similarity is calculated using Euclidean distance.
- Lower profile distance means greater statistical similarity.
- Radar-chart scores are percentiles relative to the
  player’s position.

### Limitations

- Similarity does not measure overall player quality.
- Results describe the 2025/26 season and do not predict
  future performance or transfer success.
- Broad position categories can contain different tactical roles.
- Team style, league context, age, injuries, and transfer cost
  are not included.
- Recommendations should support scouting judgment rather
  than replace video analysis.
        """
    )
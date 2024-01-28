import anvil.server

import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler  # pip install scikit-learn

from .get_iso import get_iso


def calculate_performance():
    df = pd.read_csv(anvil.server.get_app_origin() + '/_/theme/matches_1930_2022.csv')
    performance_wl = {}
    performance_goals = {}
    for index, row in df.iterrows():
        home_team = row['home_team']
        away_team = row['away_team']
        home_score = row['home_score']
        away_score = row['away_score']
        home_xg = row['home_xg']
        away_xg = row['away_xg']

        home_iso = get_iso(home_team)
        away_iso = get_iso(away_team)

        # Calculate if home team won/loss according to expectation.
        if home_score > away_score and home_xg > away_xg:
            if home_iso in performance_wl:
                performance_wl[home_iso] += 1
            else:
                performance_wl[home_iso] = 1
        elif home_score < away_score and home_xg > away_xg:
            if home_iso in performance_wl:
                performance_wl[home_iso] -= 1
            else:
                performance_wl[home_iso] = -1

        # Calculate if away team won/loss according to expectation.
        if away_score > home_score and away_xg > home_xg:
            if away_iso in performance_wl:
                performance_wl[away_iso] += 1
            else:
                performance_wl[away_iso] = 1
        elif away_score < home_score and away_xg > home_xg:
            if away_iso in performance_wl:
                performance_wl[away_iso] -= 1
            else:
                performance_wl[away_iso] = -1

            # Calculate how many goals each team scored and got scored against compared to expectation.
        if pd.notna(home_xg):
            if home_iso in performance_goals:
                performance_goals[home_iso] += (home_score - home_xg) - (away_score - away_xg)
            else:
                performance_goals[home_iso] = (home_score - home_xg) - (away_score - away_xg)

            if away_iso in performance_goals:
                performance_goals[away_iso] += (away_score - away_xg) - (home_score - home_xg)
            else:
                performance_goals[away_iso] = (away_score - away_xg) - (home_score - home_xg)

    # standardize the scores for performance_wl using minmaxscaler.
    scaler = MinMaxScaler(feature_range=(-1, 1))

    performance_wl_scores = list(performance_wl.values())
    performance_wl_scores = scaler.fit_transform(np.array(performance_wl_scores).reshape(-1, 1))

    for i, team in enumerate(performance_wl.keys()):
        performance_wl[team] = performance_wl_scores[i][0]

    performance_goals = {k: round(v, 2) for k, v in performance_goals.items()}

    return performance_wl, performance_goals

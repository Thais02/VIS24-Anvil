import math
import pandas as pd
import numpy as np

from .get_iso import get_iso


# Extract minute information from the card columns
def _extract(df, column):
    pattern = r'(?P<name>[^·]+) · (?P<minutes>\d+|\d+\+\d+)'

    result = df[column].str.extractall(pattern)
    df[column + 'num_cards'] = result.groupby(level=0).size()
    df[column + 'min_lst_away'] = result['minutes'].astype(str).groupby(level=0).agg(list)


def _extract_yellow(df, column):
    pattern_yellow_long = r'(\d+)(?:\+(\d+))?&rsquor;'

    result_yellow_long = df[column].str.extractall(pattern_yellow_long)
    df[column + '_num_cards'] = result_yellow_long.groupby(level=0).size()

    minutes_list_yellow_long = result_yellow_long[0].combine_first(result_yellow_long[1])
    minutes_list_yellow_long = minutes_list_yellow_long.replace('', '0').astype(float)
    df[column + '_min_list'] = minutes_list_yellow_long.groupby(level=0).agg(list)


def _nan(x):
    if isinstance(x, list):
        return x
    elif math.isnan(x):
        return []
    else:
        return [x]


def prep_df():
    df = pd.read_csv('_/theme/matches_1930_2022.csv')

    # Select relevant columns for analysis from the matches dataframe
    card_columns = ['home_red_card', 'away_red_card', 'home_yellow_red_card', 'away_yellow_red_card']
    yellow_cards = ['home_yellow_card_long', 'away_yellow_card_long']

    # Create a new DataFrame with only the relevant columns
    cards_df = df[card_columns].copy()
    yel_cards_df = df[yellow_cards].copy()

    for column in card_columns:
        _extract(cards_df, column)

    for column in yellow_cards:
        _extract_yellow(yel_cards_df, column)

    cards_df['away_yellow_card_long_min_list'] = yel_cards_df['away_yellow_card_long_min_list']
    cards_df['home_yellow_card_long_min_list'] = yel_cards_df['home_yellow_card_long_min_list']

    cards_df['away_yellow_card_long_num_cards'] = yel_cards_df['away_yellow_card_long_num_cards']
    cards_df['home_yellow_card_long_num_cards'] = yel_cards_df['home_yellow_card_long_num_cards']

    cards_df['Red_cards_away'] = cards_df['away_red_cardnum_cards'].fillna(0) + cards_df[
        'away_yellow_red_cardnum_cards'].fillna(0)
    cards_df['Red_cards_home'] = cards_df['home_red_cardnum_cards'].fillna(0) + cards_df[
        'home_yellow_red_cardnum_cards'].fillna(0)

    cards_df['Yellow_cards_away'] = cards_df['away_yellow_card_long_num_cards'].fillna(0) - cards_df[
        'away_yellow_red_cardnum_cards'].fillna(0)
    cards_df['Yellow_cards_home'] = cards_df['home_yellow_card_long_num_cards'].fillna(0) - cards_df[
        'home_yellow_red_cardnum_cards'].fillna(0)

    cards_df['total_cards_away'] = cards_df['Red_cards_away'].fillna(0) + cards_df['Yellow_cards_away']
    cards_df['total_cards_home'] = cards_df['Red_cards_home'] + cards_df['Yellow_cards_home']

    cards_df['total_min_away'] = yel_cards_df['away_yellow_card_long_min_list'].apply(_nan) + cards_df[
        'away_yellow_red_cardmin_lst_away'].apply(_nan) + cards_df['away_red_cardmin_lst_away'].apply(_nan)
    cards_df['total_min_home'] = yel_cards_df['home_yellow_card_long_min_list'].apply(_nan) + cards_df[
        'home_yellow_red_cardmin_lst_away'].apply(_nan) + cards_df['home_red_cardmin_lst_away'].apply(_nan)

    cards_df['total_cards'] = cards_df['total_cards_home'] + cards_df['total_cards_away']
    cards_df['total_min'] = cards_df['total_min_away'] + cards_df['total_min_home']

    df['total_cards'] = cards_df['total_cards']

    df_c = cards_df[['Red_cards_away', 'Yellow_cards_away', 'Red_cards_home', 'Yellow_cards_home']].copy()
    df_c['home_team'] = df['home_team']
    df_c['away_team'] = df['away_team']
    df_c['Year'] = df['Year']

    return df, cards_df, yel_cards_df, df_c


def total_years_total(df, cards_df, yel_cards_df):
    crds_years_df = pd.DataFrame()
    crds_years_df['Year'] = df['Year']
    crds_years_df['Red_Cards'] = cards_df['away_red_cardnum_cards'].fillna(0) + cards_df[
        'home_red_cardnum_cards'].fillna(0) + cards_df['away_yellow_red_cardnum_cards'].fillna(0) + cards_df[
                                     'home_yellow_red_cardnum_cards'].fillna(0)

    crds_years_df['Yellow_Cards'] = yel_cards_df['away_yellow_card_long_num_cards'].fillna(0) + yel_cards_df[
        'home_yellow_card_long_num_cards'].fillna(0) - cards_df['away_yellow_red_cardnum_cards'].fillna(0) - cards_df[
                                        'home_yellow_red_cardnum_cards'].fillna(0)

    df_grouped = crds_years_df.groupby('Year').sum()

    df_wc = pd.read_csv('Data/FIFA World Cup Historic/world_cup.csv')
    df_sorted = df_wc.sort_values('Year', ascending=True)
    df_sorted.set_index('Year', inplace=True)

    df_grouped['Matches'] = df_sorted['Matches']
    df_grouped['Norm_red_cards'] = df_grouped.apply(lambda x: x['Red_Cards'] / x['Matches'], axis=1)

    df_grouped['Norm_Yellow_cards'] = df_grouped['Yellow_Cards'] / df_grouped['Matches']

    df_grouped.drop('Red_Cards', axis=1, inplace=True)

    df_grouped.drop('Yellow_Cards', axis=1, inplace=True)
    df_grouped.drop('Matches', axis=1, inplace=True)

    return df_grouped


def total_years_per_country():
    data = {}  # iso : (years, reds, yellows)

    df, cards_df, yel_cards_df, df_c = prep_df()

    crds_years_df = pd.DataFrame()
    crds_years_df['Year'] = df['Year']
    crds_years_df['Red_Cards'] = cards_df['away_red_cardnum_cards'].fillna(0) + cards_df[
        'home_red_cardnum_cards'].fillna(0) + cards_df['away_yellow_red_cardnum_cards'].fillna(0) + cards_df[
                                     'home_yellow_red_cardnum_cards'].fillna(0)

    crds_years_df['Yellow_Cards'] = yel_cards_df['away_yellow_card_long_num_cards'].fillna(0) + yel_cards_df[
        'home_yellow_card_long_num_cards'].fillna(0) - cards_df['away_yellow_red_cardnum_cards'].fillna(0) - cards_df[
                                        'home_yellow_red_cardnum_cards'].fillna(0)

    crds_years_df['home_team'] = df['home_team']
    crds_years_df['away_team'] = df['away_team']

    df['RedCards'] = crds_years_df['Red_Cards']
    df['YellowCards'] = crds_years_df['Yellow_Cards']

    for country_name in set(df['home_team'].unique()).union(set(df['away_team'].unique())):
        country_data = df_c[(df_c['home_team'] == country_name) | (df_c['away_team'] == country_name)].copy()
        country_data['Red_cards_country'] = np.where(country_data['away_team'] == country_name,
                                                     country_data['Red_cards_away'], 0) + \
                                            np.where(country_data['home_team'] == country_name,
                                                     country_data['Red_cards_home'], 0)
        country_data['Yellow_cards_country'] = np.where(country_data['away_team'] == country_name,
                                                        country_data['Yellow_cards_away'], 0) + \
                                               np.where(country_data['home_team'] == country_name,
                                                        country_data['Yellow_cards_home'], 0)

        country_data = country_data.groupby('Year').sum(numeric_only=True)

        years = country_data.index.to_list()
        Red_cards_country = country_data['Red_cards_country'].to_list()
        Yellow_cards_country = country_data['Yellow_cards_country'].to_list()
        for year in range(1930, 2022 + 1, 4):
            if year not in years:
                years.append(year)
                Red_cards_country.append(0)
                Yellow_cards_country.append(0)

        data[get_iso(country_name)] = (years, Red_cards_country, Yellow_cards_country)

    return data


def country_statistics_extended():
    df = pd.read_csv('_/theme/matches_1930_2022.csv')
    data = {}  # iso : dict
    for country_name in set(df['home_team'].unique()).union(set(df['away_team'].unique())):
        # Filter matches for the specified country
        country_matches_home = df[df['home_team'] == country_name]
        country_matches_away = df[df['away_team'] == country_name]

        country_matches_home = country_matches_home.copy()
        country_matches_home.loc[:, 'winner'] = country_matches_home.apply(
            lambda row: row['home_team'] if (row['home_score'] > row['away_score']) or (
                    row['home_score'] == row['away_score'] and row['home_penalty'] > row['away_penalty']) else
            (row['away_team'] if (row['home_score'] < row['away_score']) or (
                    row['home_score'] == row['away_score'] and row['home_penalty'] < row['away_penalty']) else None),
            axis=1)

        country_matches_away = country_matches_away.copy()
        country_matches_away.loc[:, 'winner'] = country_matches_away.apply(
            lambda row: row['away_team'] if (row['home_score'] < row['away_score']) or (
                    row['home_score'] == row['away_score'] and row['home_penalty'] < row['away_penalty']) else
            (row['home_team'] if (row['home_score'] > row['away_score']) or (
                    row['home_score'] == row['away_score'] and row['home_penalty'] > row['away_penalty']) else None),
            axis=1)

        # Total Wins, losses, draws for Home Matches
        total_home_wins = country_matches_home['winner'].eq(country_matches_home['home_team']).sum()
        total_home_losses = country_matches_home['winner'].eq(country_matches_home['away_team']).sum()
        total_home_draws = country_matches_home['winner'].isna().sum()

        # Total Wins, losses, draws for Away Matches
        total_away_wins = country_matches_away['winner'].eq(country_matches_away['away_team']).sum()
        total_away_losses = country_matches_away['winner'].eq(country_matches_away['home_team']).sum()
        total_away_draws = country_matches_away['winner'].isna().sum()

        country_matches = pd.concat([country_matches_home, country_matches_away])

        total_matches = len(country_matches)
        total_wins = total_away_wins + total_home_wins
        total_losses = total_home_losses + total_away_losses
        total_draws = total_home_draws + total_away_draws

        # For home matches
        goals_scored_home = country_matches_home['home_score'].sum()
        goals_conceded_home = country_matches_home['away_score'].sum()

        # For away matches
        goals_scored_away = country_matches_away['away_score'].sum()
        goals_conceded_away = country_matches_away['home_score'].sum()

        # Total goals scored and conceded
        total_goals_scored = goals_scored_home + goals_scored_away
        total_goals_conceded = goals_conceded_home + goals_conceded_away

        win_loss_ratio = total_wins / total_losses if total_losses != 0 else "Infinity"
        home_win_loss_ratio = total_home_wins / total_home_losses if total_home_losses != 0 else float('inf')
        away_win_loss_ratio = total_away_wins / total_away_losses if total_away_losses != 0 else float('inf')

        # Count unique instances of 'Semi-Final'
        semi_finals_count = country_matches.drop_duplicates(subset=['Year', 'Round'])['Round'].eq('Semi-finals').sum()

        # Count unique instances of 'Quarter Final'
        quarter_finals_count = country_matches.drop_duplicates(subset=['Year', 'Round'])['Round'].eq(
            'Quarter-finals').sum()

        # Count unique instances of 'Final'
        unique_finals_count = country_matches.drop_duplicates(subset=['Year', 'Round'])['Round'].eq('Final') | \
                              country_matches.drop_duplicates(subset=['Year', 'Round'])['Round'].eq('Final stage')
        finals_count = unique_finals_count.sum()

        # Count how many times the country won the World Cup (i.e., won the final)
        world_cup_wins = country_matches[country_matches['winner'] == country_name]['Round'].eq(
            'Final' or 'Final stage').sum()

        data[get_iso(country_name)] = list({
                                               'World Cup wins': int(world_cup_wins),
                                               'Finals count': int(finals_count),
                                               'Semi-finals count': int(semi_finals_count),
                                               'Quarter-finals count': int(quarter_finals_count),
                                               'Total Matches': int(total_matches),
                                               'Total Wins': int(total_wins),
                                               'Total Losses': int(total_losses),
                                               'Total Draws': int(total_draws),
                                               'Goals Scored': int(total_goals_scored),
                                               'Goals Conceded': int(total_goals_conceded),
                                               'Win-Loss Ratio': float(round(win_loss_ratio, 2)),
                                               'Home win-Loss Ratio': float(round(home_win_loss_ratio, 2)),
                                               'Away win-Loss Ratio': float(round(away_win_loss_ratio, 2)),
                                           }.items())

    return data


def get_cards_corr():
    df, cards_df, yel_cards_df, df_c = prep_df()
    return total_years_total(df, cards_df, yel_cards_df)

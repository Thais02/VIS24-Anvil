import anvil.server

import pycountry

import plotly.express as px

import pandas as pd
import numpy as np
from collections import Counter

from .get_iso import get_iso, get_name, get_iso_name
from .xpectedvsreality import calculate_performance
from .cards_corr import get_cards_corr, country_statistics_extended, total_years_per_country


class Config:
    def __init__(
            self,
            colorscale='Reds',  # see https://plotly.com/python/builtin-colorscales/
            reversescale=False,  # reverse the colorscale
            colorbar_title='Goals',
            plot_map_layout_title='Total amount of goals scored per country',
            plot_bar_layout_title='Top 5',
    ):
        self.colorscale = colorscale
        self.reversescale = reversescale
        self.colorbar_title = colorbar_title
        self.plot_map_layout_title = plot_map_layout_title
        self.plot_bar_layout_title = plot_bar_layout_title


def get_goals_data():
    df_full = pd.read_csv(anvil.server.get_app_origin() + '/_/theme/matches_1930_2022.csv')

    # dictionary with years as keys. For each year has a tuple of:
    # - list of the iso alpha_3 strings of the ALL countries (countries who did not participate/score get a value of 0)
    # - list of the amount of goals made
    # - list of the full country names, retrieved from pycountry for consistency
    # - dictionary with country names as keys and amount of goals as values, for the top-5 only
    data = {}  # {year: (country_iso's, goals, country_names, {country_name: goals})}

    for year in range(1930, 2022 + 1, 4):
        if year in [1942, 1946]:
            data[str(year)] = ([], [0], [], [])
            continue

        df = df_full[df_full['Date'].str.contains(str(year))]

        goals = {}  # {country_iso: goals}

        for row in df.iterrows():
            iso = get_iso(row[1]['home_team'])
            goals[iso] = goals.get(iso, 0) + row[1]['home_score']
            iso = get_iso(row[1]['away_team'])
            goals[iso] = goals.get(iso, 0) + row[1]['away_score']

        list_iso = []
        list_goals = []
        list_countries = []
        for iso, num_goals in goals.items():
            list_iso.append(iso)
            list_goals.append(num_goals)
            try:
                # try common_name first if it exists, else name
                list_countries.append(pycountry.countries.get(alpha_3=iso).common_name)
            except:
                list_countries.append(pycountry.countries.get(alpha_3=iso).name)

        top5 = {}
        for iso, goals in Counter(goals).most_common(5):
            # store the top-5 in order to make the website faster
            try:
                top5[pycountry.countries.get(alpha_3=iso).common_name] = goals
            except:
                top5[pycountry.countries.get(alpha_3=iso).name] = goals

        data[str(year)] = (list_iso, list_goals, list_countries, top5)

    config = Config()
    return data, config


def get_xg_xp(vis_name):
    performance_wl, performance_goals = calculate_performance()
    dic = performance_goals if vis_name == 'xg' else performance_wl

    config = Config(
        colorbar_title='Goals' if vis_name == 'xg' else 'Winrate',
        plot_map_layout_title='Actual versus predicted goals scored' if vis_name == 'xg' else 'Actual versus predicted winrate',
        colorscale='RedBlue',
    )

    isos = []
    nums = []
    countries = []
    for iso, num in dic.items():
        isos.append(iso)
        nums.append(float(num))
        countries.append(get_name(iso))

    top5 = {}
    for iso, num in Counter(dic).most_common(5):
        # store the top-5 in order to make the website faster
        top5[get_name(iso)] = float(num)

    return {'2018': (isos, nums, countries, top5)}, config


def get_cards_data():
    df = get_cards_corr()
    Norm_red_cards = [round(x, 2) for x in df['Norm_red_cards'].to_list()]
    Norm_Yellow_cards = [round(x, 2) for x in df['Norm_Yellow_cards'].to_list()]

    data = (df.index.to_list(), Norm_red_cards, Norm_Yellow_cards)

    config = Config()

    return data, config


def get_finish_data():
    blacklist = ['ATA']
    df_full = pd.read_csv(anvil.server.get_app_origin() + '/_/theme/matches_1930_2022.csv')

    round_order = {
        'Group stage': 1,
        'Round of 16': 2,
        'Quarter-finals': 3,
        'Semi-finals': 4,
        'Third-place match': 5,
        'Final': 6,
    }

    # Standardize group names because some years have a different name for a particular round
    df_full.loc[df_full['Round'] == 'First round', 'Round'] = 'Group stage'  # 1974 + 1978 first round equivalent to group stage
    df_full.loc[df_full['Round'] == 'Second round', 'Round'] = 'Semi-finals'  # 1974 + 1978 second round equivalent to semi-finals
    df_full.loc[df_full['Round'] == 'First group stage', 'Round'] = 'Group stage'  # 1982 first group stage equivalent to group stage
    df_full.loc[df_full['Round'] == 'Second group stage', 'Round'] = 'Group stage'  # 1982 second group stage equivalent to group stage
    df_full.loc[df_full['Round'] == 'Group stage play-off', 'Round'] = 'Group stage'  # 1954 + 1958 group stage play-off equivalent to group stage
    df_full.loc[df_full['Round'] == 'Final stage', 'Round'] = 'Final'  # 1950 special case (winner determined over multiple games)

    data = {}  # {year: (country_iso's, reached_order, country_names, reached_rounds)}

    for year in range(1930, 2022 + 1, 4):
        df = df_full[df_full['Year'] == year]

        isos = []
        reached_orders = []
        country_names = []
        reached_rounds = []

        for country_name in set(df['home_team'].unique()).union(set(df['away_team'].unique())):
            df_h = df[df['home_team'] == country_name]
            df_a = df[df['away_team'] == country_name]
            res_h = df_h['Round']
            res_a = df_a['Round']
            reached_round = res_h.to_list()
            reached_round.extend(res_a.to_list())
            reached_order = [round_order.get(item, 0) for item in reached_round]
            max_i = reached_order.index(max(reached_order))

            iso, name = get_iso_name(country_name)
            isos.append(iso)
            reached_orders.append(max(reached_order))
            country_names.append(name)
            reached_rounds.append(reached_round[max_i])

        for country in pycountry.countries:
            # add all other countries with 0, so they still appear on the map
            if country.alpha_3 not in blacklist and country.alpha_3 not in isos:
                isos.append(country.alpha_3)
                reached_orders.append(0)
                country_names.append(get_name(country.alpha_3))
                reached_rounds.append('Did not participate')

        data[str(year)] = (isos, reached_orders, country_names, reached_rounds)

    config = Config(
        plot_map_layout_title='Highest round reached',
        colorbar_title='Round'
    )
    return data, config


def get_scatter_data():
    # Read the data from csv file and select only columns relevant for multivariate scatter plot
    df = pd.read_csv(anvil.server.get_app_origin() + '/_/theme/matches_1930_2022.csv')
    df_new = df[
        ['home_team', 'away_team', 'home_score', 'away_score', 'Round', 'Year', 'home_penalty', 'away_penalty']].copy()

    # Standardize group names because some years have a different name for a particular round
    df_new.loc[
        df['Round'] == 'First round', 'Round'] = 'Group stage'  # 1974 + 1978 first round equivalent to group stage
    df_new.loc[
        df['Round'] == 'Second round', 'Round'] = 'Semi-finals'  # 1974 + 1978 second round equivalent to semi-finals
    df_new.loc[
        df['Round'] == 'First group stage', 'Round'] = 'Group stage'  # 1982 first group stage equivalent to group stage
    df_new.loc[df[
                   'Round'] == 'Second group stage', 'Round'] = 'Group stage'  # 1982 second group stage equivalent to group stage
    df_new.loc[df[
                   'Round'] == 'Group stage play-off', 'Round'] = 'Group stage'  # 1954 + 1958 group stage play-off equivalent to group stage
    df_new.loc[df['Round'] == 'Final stage', 'Round'] = 'Final'  # 1950 special case (winner determined over multiple games)

    # For each match/row, add a row to dataframe where home team is equal to away team and vice versa (makes plotting easier)
    for row_as_tuple in df_new.itertuples(index=False):
        home_team, away_team, home_score, away_score, Round, Year, home_penalty, away_penalty = row_as_tuple
        new_row = {'home_team': [away_team], 'away_team': [home_team], 'home_score': [away_score],
                   'away_score': [home_score], 'Round': [Round], 'Year': [Year], 'home_penalty': [away_penalty],
                   'away_penalty': [home_penalty]}
        df_new = pd.concat([df_new, pd.DataFrame(new_row)], ignore_index=True)

    # Create new column which contains the outcome of the match wrt the home team (win, loss or draw)
    conditions = [(df_new['home_score'] > df_new['away_score']) | (df_new['home_penalty'] > df_new['away_penalty']),
                  (df_new['away_score'] > df_new['home_score']) | (df_new['away_penalty'] > df_new['home_penalty']),
                  (df_new['home_score'] == df_new['away_score']) & (np.isnan(df_new['home_penalty']))]
    choices = ['Win', 'Loss', 'Draw']
    df_new['Outcome'] = np.select(conditions, choices)

    # Create new column which contains the goal difference of the match
    conditions2 = [df_new['home_penalty'].notnull(), df_new['home_penalty'].isnull()]
    choices2 = [df_new['home_penalty'] - df_new['away_penalty'], df_new['home_score'] - df_new['away_score']]
    df_new['Goal difference'] = np.select(conditions2, choices2)

    # Create new column for marker size depending on goal diff (size must be >0).
    # Take absolute value so there are no negative values and add 1 so no 0 values
    df_new['goal_diff_size'] = abs(df_new['Goal difference']) + 1

    # Add jitter to x-axis (year) to reduce overlap of data
    df_new['year_jittered'] = df_new['Year'] + np.random.uniform(-1, 1, df_new.shape[0])

    # Define mapping for your categories to integers
    categories = ['Group stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Third-place match', 'Final']
    mapping = {category: i for i, category in enumerate(categories)}

    # Map 'Round' to integers and add jitter
    df_new['Round_jittered'] = df_new['Round'].map(mapping) + np.random.uniform(-0.5, 0.5, df_new.shape[0])

    # Color map based on outcome
    color_discrete_map = {'Win': 'green', 'Loss': 'red', 'Draw': 'blue'}

    data = {}  # iso : fig.to_dict()

    for country_name in set(df['home_team'].unique()).union(set(df['away_team'].unique())):
        # Update figure based on country selected in dropdown menu
        filter_df = df_new[df_new.home_team == country_name].copy()

        # Create plot
        fig = px.scatter(filter_df,
                         x='year_jittered',
                         y='Round_jittered',
                         color='Outcome',
                         size='goal_diff_size',
                         opacity=0.5,
                         color_discrete_map=color_discrete_map,
                         custom_data=['Year', 'Outcome', 'Goal difference', 'Round', 'away_team'],
                         )

        # Update yaxis labels
        fig.update_yaxes(tickvals=list(mapping.values()), ticktext=list(mapping.keys()))

        fig.update_traces(
            hovertemplate="<br>".join([
                "Year: %{customdata[0]}",
                "Round: %{customdata[3]}",
                "Opponent: %{customdata[4]}",
                "Outcome: %{customdata[1]}",
                "Goal difference: %{customdata[2]}"
            ])
        )

        fig.update_xaxes(
            range=[1928, 2024],
            tickvals=np.arange(1930, 2023, 4),
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Round"
        )

        data[get_iso(country_name)] = fig.to_dict()

    return data


def get_general_data():
    df = pd.read_csv(anvil.server.get_app_origin() + '/_/theme/world_cup.csv').set_index('Year')
    return df.set_index(df.index.astype(str)).to_dict('index')


def get_country_stats(vis_name):
    df_full = pd.read_csv(anvil.server.get_app_origin() + '/_/theme/matches_1930_2022.csv')

    data = {}  # {year: {country_iso: {keys: values}}}

    if vis_name in ['xg', 'xp']:
        df = df_full[df_full['Year'].isin([2018, 2022])]
        year_dict = {}
        # count the total number of matches played by each country this year
        counter_home = Counter(df['home_team'])
        counter_away = Counter(df['away_team'])
        all_country_names = set(counter_home.keys()).union(set(counter_away.keys()))

        for country_name in all_country_names:
            # find team manager and captain, assumes consistency within year
            try:
                row = df[df['away_team'] == country_name].iloc[0]
            except:
                row = df[df['away_team'] == country_name]
            manager = row['away_manager']
            captain = row['away_captain']
            if not isinstance(manager, str):
                try:
                    row = df[df['home_team'] == country_name].iloc[0]
                except:
                    row = df[df['home_team'] == country_name]
                manager = row['home_manager']
                captain = row['home_captain']

            country_dict = {'Total matches': counter_home.get(country_name, 0) + counter_away.get(country_name, 0),
                            'Home matches': counter_home.get(country_name, 0),
                            'Away matches': counter_away.get(country_name, 0),
                            'Team manager': manager,
                            'Team captain': captain
                            }

            year_dict[get_iso(country_name)] = country_dict

        # add all other countries with N/A data
        for country in pycountry.countries:
            if country.alpha_3 not in year_dict:
                year_dict[country.alpha_3] = {'Did not participate': ''}

        data['2018'] = year_dict
    else:
        for year in range(1930, 2022 + 1, 4):
            year_dict = {}

            df = df_full[df_full['Year'] == year]

            # count the total number of matches played by each country this year
            counter_home = Counter(df['home_team'])
            counter_away = Counter(df['away_team'])
            all_country_names = set(counter_home.keys()).union(set(counter_away.keys()))

            for country_name in all_country_names:
                # find team manager and captain, assumes consistency within year
                try:
                    row = df[df['away_team'] == country_name].iloc[0]
                except:
                    row = df[df['away_team'] == country_name]
                manager = row['away_manager']
                captain = row['away_captain']
                if not isinstance(manager, str):
                    try:
                        row = df[df['home_team'] == country_name].iloc[0]
                    except:
                        row = df[df['home_team'] == country_name]
                    manager = row['home_manager']
                    captain = row['home_captain']

                country_dict = {'Total matches': counter_home.get(country_name, 0) + counter_away.get(country_name, 0),
                                'Home matches': counter_home.get(country_name, 0),
                                'Away matches': counter_away.get(country_name, 0),
                                'Team manager': manager,
                                'Team captain': captain
                                }

                year_dict[get_iso(country_name)] = country_dict

            # add all other countries with N/A data
            for country in pycountry.countries:
                if country.alpha_3 not in year_dict:
                    year_dict[country.alpha_3] = {'Did not participate': ''}

            data[str(year)] = year_dict

    return data


@anvil.server.callable
def get_data(vis_name):
    if vis_name == 'pos':
        data, config = get_finish_data()
    elif vis_name == 'goals':
        data, config = get_goals_data()
    elif vis_name in ['xg', 'xp']:
        data, config = get_xg_xp(vis_name)
    elif vis_name == 'cards':
        data, config = get_cards_data()
    else:
        raise Exception(f'visualisation "{vis_name}" not supported by SERVER')

    return data, config.__dict__, get_country_stats(vis_name)


@anvil.server.callable
def get_static_data():
    return get_general_data(), country_statistics_extended(), total_years_per_country(), get_scatter_data()

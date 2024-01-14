import anvil.server

import pandas as pd
from collections import Counter

import pycountry

def get_iso(name):
    isos = {
    'Russia': 'RUS',
    'IR Iran': 'IRN',
    'Korea Republic': 'KOR',  # south korea
    'Korea DPR': 'PRK',  # best korea
    'Czech Republic': 'CZE',
    'Türkiye': 'TUR',
    'Republic of Ireland': 'IRL',
    'China PR': 'CHN',
    'Bolivia': 'BOL',
    'Zaire': 'COD',  # Democratic Congo
    'Dutch East Indies': 'IDN',  # Indonesia
    # All English teams are combined as Great Britain
    'England': 'GBR',
    'Wales': 'GBR',
    'Scotland': 'GBR',
    'Northern Ireland': 'GBR',
    # Both halves of Germany are combined
    'West Germany': 'DEU',
    'Germany DR': 'DEU',
    # Montenegro is tiny so treat it as just Serbia
    'Serbia and Montenegro': 'SRB',
    # Fell apart in many countries but former capital became Serbia
    'FR Yugoslavia': 'SRB',  # Serbia
    'Yugoslavia': 'SRB',  # Serbia
    # Idem with this former country
    'Czechoslovakia': 'CZE',  # Czech Republic
    # Soviet Union football team has been combined with Russia
    'Soviet Union': 'RUS',
    }
    try:
        iso = pycountry.countries.get(name=name).alpha_3
    except:
        iso = isos.get(name)
    return iso

def get_country_stats(df_full):
    data = {}  # {year: {country_iso: {keys: values}}}

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
    if vis_name == 'goals':
        blacklist = ['ATA']
        df_full = pd.read_csv('https://vis.thijsblom.xyz/_/theme/matches_1930_2022.csv')
    
        # dictionary with years as keys. For each year has a tuple of:
        # - list of the iso alpha_3 strings of the ALL countries (countries who did not participate/score get a value of 0)
        # - list of the amount of goals made
        # - list of the full country names, retrieved from pycountry for consistency
        # - dictionary with country names as keys and amount of goals as values, for the top-5 only
        data = {}  # {year: (country_iso's, goals, country_names, {country_name: goals})}
        
        for year in range(1930, 2022+1, 4):
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
                list_countries.append(pycountry.countries.get(alpha_3=iso).name)
            for country in pycountry.countries:
                if country.alpha_3 not in blacklist and country.alpha_3 not in list_iso:
                    list_iso.append(country.alpha_3)
                    list_goals.append(0)
                    list_countries.append(country.name)
            top5 = {}
            for iso, goals in Counter(goals).most_common(5):
                top5[pycountry.countries.get(alpha_3=iso).name] = goals
        
            data[str(year)] = (list_iso, list_goals, list_countries, top5)

        general_data = pd.read_csv('https://vis.thijsblom.xyz/_/theme/world_cup.csv').set_index('Year')
        country_stats = get_country_stats(df_full)
        
        return data, None, general_data.set_index(general_data.index.astype(str)).to_dict('index'), country_stats
    else:
        raise Exception('Not implemented by server')

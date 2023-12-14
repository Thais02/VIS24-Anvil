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
        
        return data, None, general_data.set_index(general_data.index.astype(str)).to_dict('index')
    else:
        raise Exception('Not implemented by server')

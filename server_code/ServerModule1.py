import anvil.server
import pandas as pd

@anvil.server.callable
def get_data():
    data = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_with_codes.csv')
    print(data.head())
    data.drop_duplicates(subset=['iso_alpha'], keep='first', inplace=True)
    return list(data['iso_alpha']), list(data['gdpPercap'])



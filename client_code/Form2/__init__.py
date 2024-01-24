from ._anvil_designer import Form2Template
from anvil import *
import anvil.server

import plotly.graph_objects as go

class Form2(Form2Template):
    def __init__(self, dic, cards_data, country='', **properties):
        self.init_components(**properties)

        years, reds, yellows = cards_data

        self.plot.layout = {'barmode': 'stack'}
        self.plot.layout.xaxis.tick0 = 1930
        self.plot.layout.xaxis.dtick = 4
        self.plot.layout.xaxis.title = 'Year'
        self.plot.layout.yaxis.title = 'Total number of cards'

        self.plot.layout.title = "Red and yellow cards per year"
        
        self.plot.data = [
            go.Bar(name='Red cards', x=years, y=reds, marker={'color': '#DA291C'}, selectedpoints=[0]),
            go.Bar(name='Yellow cards', x=years, y=yellows, marker={'color': '#FFC72C'}, selectedpoints=[0])
        ]

        self.richtext_side.content = f'|{country}|1930 - 2022|\n| --- | ---: |\n'
        for key, value in dic:
            self.richtext_side.content += f'| **{key}** | {value} |\n'

    def plot_click(self, points, **event_args):
        print(points)

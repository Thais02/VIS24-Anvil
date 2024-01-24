from ._anvil_designer import Form2Template
from anvil import *
import anvil.server

import plotly.graph_objects as go

class Form2(Form2Template):
    def __init__(self, dic, cards_data, country='', year=None, **properties):
        self.dic = dic
        self.years, self.reds, self.yellows = cards_data
        self.country = country
        self.init_components(**properties)
        self.update(year=year)

    def update(self, year=None):
        if year:
            try:
                index = self.years.index(year)
            except ValueError:
                index = None

        self.plot.layout = {'barmode': 'stack'}
        self.plot.layout.xaxis.tick0 = 1930
        self.plot.layout.xaxis.dtick = 4
        self.plot.layout.xaxis.title = 'Year'
        self.plot.layout.yaxis.title = 'Total number of cards'

        self.plot.layout.title = "Red and yellow cards per year"
        
        self.plot.data = [
            go.Bar(name='Red cards', x=self.years, y=self.reds, marker={'color': '#DA291C'}, selectedpoints=[index] if year and index else False),
            go.Bar(name='Yellow cards', x=self.years, y=self.yellows, marker={'color': '#FFC72C'}, selectedpoints=[index] if year and index else False)
        ]

        self.richtext_side.content = f'|{self.country}|1930 - 2022|\n| --- | ---: |\n'
        for key, value in self.dic:
            self.richtext_side.content += f'| **{key}** | {value} |\n'

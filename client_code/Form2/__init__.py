from ._anvil_designer import Form2Template
from anvil import *
import anvil.server

import plotly.graph_objects as go

class Form2(Form2Template):
    def __init__(self, dic, cards_data, country='', year=None, **properties):
        self.dic = dic
        self.years, self.reds, self.yellows = cards_data
        self.country = country

        for year_iter in range(1930, 2022 + 1, 4):
            if year_iter not in self.years:
                self.years.append(year_iter)
                self.reds.append(0)
                self.yellows.append(0)
        
        self.init_components(**properties)
        self.update(year=year)

    def update(self, year=None):
        index = None
        if year:
            if isinstance(year, int):
                try:
                    index = self.years.index(year)
                except ValueError:
                    index = None
            else:
                index = []
                for y in range(year[0], year[1]+1, 4):
                    try:
                        i = self.years.index(year)
                        index.append(i)
                    except ValueError:
                        pass

        print(year, index, list(range(year[0], year[1]+1, 4)))
        selectedpoints = False
        if year and index is not None:
            if isinstance(year, int):
                if self.reds[index] or self.yellows[index]:
                    selectedpoints = [index]
            else:
                for i in index:
                    if self.reds[i] or self.yellows[i]:
                        selectedpoints = index
                        break
            

        self.plot.layout = {'barmode': 'stack'}
        self.plot.layout.xaxis.tick0 = 1930
        self.plot.layout.xaxis.dtick = 4
        self.plot.layout.xaxis.title = 'Year'
        self.plot.layout.yaxis.title = 'Total number of cards'

        self.plot.layout.title = "Red and yellow cards per year"
        
        self.plot.data = [
            go.Bar(name='Red cards', x=self.years, y=self.reds, marker={'color': '#DA291C'}, selectedpoints=selectedpoints),
            go.Bar(name='Yellow cards', x=self.years, y=self.yellows, marker={'color': '#FFC72C'}, selectedpoints=selectedpoints)
        ]

        self.richtext_side.content = f'|{self.country}|1930 - 2022|\n| --- | ---: |\n'
        for key, value in self.dic:
            self.richtext_side.content += f'| **{key}** | {value} |\n'

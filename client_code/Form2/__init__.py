from ._anvil_designer import Form2Template
from anvil import *
import plotly.graph_objects as go
import anvil.server

class Form2(Form2Template):
    def __init__(self, dic, country='', **properties):
        self.init_components(**properties)

        self.plot_1.layout.title = country
        self.plot_1.data = go.Bar(x=[1,2,3,4,5], y=[2,4,8,16,32])

        self.richtext_side.content = f'|{country}|1930 - 2022|\n| --- | ---: |\n'
        for key, value in dic:
            self.richtext_side.content += f'| **{key}** | {value} |\n'

from ._anvil_designer import Form2Template
from anvil import *
import plotly.graph_objects as go
import anvil.server

class Form2(Form2Template):
    def __init__(self, country='', **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        self.plot_1.layout.title = country
        self.plot_1.data = go.Bar(x=[1,2,3,4,5], y=[2,4,8,16,32])
        
        # Any code you write here will run before the form opens.

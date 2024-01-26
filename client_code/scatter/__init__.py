from ._anvil_designer import scatterTemplate
from anvil import *
import anvil.server

import plotly.graph_objects as go

class scatter(scatterTemplate):
    def __init__(self, fig, **properties):
        self.init_components(**properties)

        self.plot_1.figure = fig

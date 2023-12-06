from ._anvil_designer import Form1Template
from anvil import *
import plotly.graph_objects as go

class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def type_button_click(self, sender, **event_args):
        self.button_vs.role = ''
        self.button_poule.role = ''
        self.button_hist.role = ''
        sender.role = 'primary-color'
        self.refresh_data_bindings()

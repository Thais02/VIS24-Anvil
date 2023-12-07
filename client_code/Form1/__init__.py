from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import plotly.graph_objects as go

class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # self.plot_1.data = go.Bar(x=list(range(2, 40, 2)), y=list(range(2, 40, 2)), name='Example interactive plot')
        locs, z, countries = anvil.server.call('get_data')
        self.plot_map.data = go.Choropleth(locations=locs, z=z, text=countries,
                    title='Total amount of goals scored per country',
                    colorscale = 'Blues',
                    autocolorscale=False,
                    reversescale=True,
                    marker_line_color='darkgray',
                    marker_line_width=0.5,
                    # colorbar_tickprefix = '$',
                    colorbar_title = 'Goals scored')
        self.plot_map.layout.geo = {'showframe': False, 'showcoastlines': False, 'projection_type': 'equirectangular'}
        # Any code you write here will run before the form opens.

    def type_button_click(self, sender, **event_args):
        self.button_vs.role = ''
        self.button_poule.role = ''
        self.button_hist.role = ''
        sender.role = 'primary-color'
        self.refresh_data_bindings()

    def slider_1_change(self, level, **event_args):
        self.refresh_data_bindings()

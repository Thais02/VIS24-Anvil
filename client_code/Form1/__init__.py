from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import plotly.graph_objects as go

class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.

    def refresh_map(self):
        isos, goals, countries, top5 = self.data[str(int(self.slider_1.level))]
        top5_x = list(top5.values())
        top5_x.reverse()
        top5_y = list(top5.keys())
        top5_y.reverse()
        map = go.Choropleth(locations=isos, z=goals, text=countries,
                    title = 'Total amount of goals scored per country',
                    colorscale = 'Reds',
                    autocolorscale = True,
                    reversescale = False,
                    marker_line_color = 'darkgray',
                    marker_line_width = 0.5,
                    colorbar_title = 'Goals scored')
        bars = go.Bar(x=top5_x, y=top5_y, name='Top 5', orientation='h', marker={
            'color': top5_x,
            'colorscale': 'Reds',
            'cmin': min(goals),
            'cmax': max(goals),
        })
        self.plot_map.data = map
        self.plot_map.layout.geo = {'showframe': False, 'showcoastlines': False, 'projection_type': 'equirectangular'}
        self.plot_bar.data = bars
        

    def slider_1_change(self, **event_args):
        self.refresh_data_bindings()
        self.refresh_map()

    def form_show(self, **event_args):
        with Notification('Fetching data...', title='Please wait'):
            self.data = anvil.server.call('get_data')
            self.refresh_map()
            self.plot_map.redraw()

    def button_play_click(self, **event_args):
        if self.button_play.icon == 'fa:play':
            self.timer.interval = 1
            self.button_play.icon = 'fa:pause'
        else:
            self.timer.interval = 0
            self.button_play.icon = 'fa:play'

    def timer_tick(self, **event_args):
        if self.slider_1.level + 4 == 1942 or self.slider_1.level + 4 == 1946:
            self.slider_1.level = 1950
        elif self.slider_1.level + 4 > 2022:
            self.slider_1.level = 1930
        else:
            self.slider_1.level += 4
        self.slider_1_change()
            

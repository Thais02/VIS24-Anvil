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
        isos, goals, countries, top5 = self.data[str(int(self.slider.value))]
        top5_x = list(top5.values())
        top5_x.reverse()
        top5_y = list(top5.keys())
        top5_y.reverse()
        map = go.Choropleth(locations=isos, z=goals, text=countries,
                    colorscale = 'Reds',
                    autocolorscale = True,
                    reversescale = False,
                    marker_line_color = 'darkgray',
                    marker_line_width = 0.5,
                    colorbar_title = 'Goals scored')
        bars = go.Bar(x=top5_x, y=top5_y,
                      orientation='h',
                      marker={
                        'color': top5_x,
                        'colorscale': 'Reds',
                        'cmin': min(goals),
                        'cmax': max(goals),
        })
        
        self.plot_map.data = map
        self.plot_map.layout.geo = {'showframe': False, 'showcoastlines': False, 'projection_type': 'equirectangular'}
        self.plot_map.layout.title = 'Total amount of goals scored per country'
        
        self.plot_bar.data = bars
        self.plot_bar.layout.title = 'Top 5'

    def form_show(self, **event_args):
        with Notification('Fetching data...', title='Please wait'):
            try:
                self.data = anvil.server.call('get_data_uplink')
                Notification('Retrieved data from connected local source', title='Data fetched', style='success', timeout=6).show()
            except:
                self.data = anvil.server.call('get_data')
        self.refresh_map()
        self.plot_map.redraw()
        self.plot_bar.redraw()

    def button_play_click(self, **event_args):
        if self.button_play.icon == 'fa:play':
            self.timer.interval = 1
            self.button_play.icon = 'fa:pause'
        else:
            self.timer.interval = 0
            self.button_play.icon = 'fa:play'

    def timer_tick(self, **event_args):
        if self.slider.value + 4 == 1942 or self.slider.value + 4 == 1946:
            self.slider.value = 1950
        elif self.slider.value + 4 > 2022:
            self.slider.value = 1930
        else:
            self.slider.value += 4
        self.slider_change(None)

    def slider_change(self, handle, **event_args):
        self.refresh_data_bindings()
        self.refresh_map()
        
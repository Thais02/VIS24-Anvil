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
        isos, goals, countries, top5 = self.data[str(int(self.slider_single.value))]
        top5_x = list(top5.values())
        top5_x.reverse()
        top5_y = list(top5.keys())
        top5_y.reverse()
        map = go.Choropleth(locations=isos, z=goals, text=countries,
                    colorscale = 'Reds',
                    autocolorscale = True,
                    reversescale = True,
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
                anvil.server.call('ping_uplink')
            except:
                self.data = anvil.server.call('get_data')
            else:
                self.data = anvil.server.call('get_data_uplink')
                Notification('Retrieved data from connected local source', title='Data fetched', style='success', timeout=6).show()
                
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
        if self.slider_single.value + 4 == 1942 or self.slider_single.value + 4 == 1946:
            self.slider_single.value = 1950
        elif self.slider_single.value + 4 > 2022:
            self.slider_single.value = 1930
        else:
            self.slider_single.value += 4
        self.slider_single_change(None)

    def slider_single_change(self, handle, **event_args):
        self.refresh_data_bindings()
        self.refresh_map()

    def checkbox_multiselect_change(self, **event_args):
        if self.checkbox_multiselect.checked:
            self.slider_multi.values = [self.slider_single.value, min(2022, self.slider_single.value+4)]
            self.slider_single.visible = False
            self.slider_multi.visible = True
        else:
            self.slider_single.value = self.slider_multi.value
            self.slider_multi.visible = False
            self.slider_single.visible = True
            
from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import plotly.graph_objects as go

from collections import Counter

class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.

    def refresh_map(self):
        if self.checkbox_multiselect.checked:
            data = {}
            iso_to_name = {}
            for year in range(int(self.slider_multi.values[0]), int(self.slider_multi.values[1])+1, 4):
                isos, nums, countries, top5 = self.data[str(year)]
                for iso, num, country in zip(isos, nums, countries):
                    lst = data.get(iso, [])
                    lst.append(num)
                    data[iso] = lst
                    iso_to_name[iso] = country
            isos = list(data.keys())
            nums = [sum(val)/len(val) for val in data.values()]
            countries = [iso_to_name[iso] for iso in data.keys()]
            top5 = {}
            for iso, num in Counter({iso: num for iso, num in zip(isos, nums)}).most_common(5):
                top5[iso_to_name[iso]] = num
        else:
            isos, nums, countries, top5 = self.data[str(int(self.slider_single.value))]
        
        top5_x = list(top5.values())
        top5_x.reverse()
        top5_y = list(top5.keys())
        top5_y.reverse()
        
        map = go.Choropleth(locations=isos, z=nums, text=countries,
                    colorscale = self.colorscale.text,
                    autocolorscale = self.autocolorscale.checked,
                    reversescale = self.reversescale.checked,
                    marker_line_color = 'darkgray',
                    marker_line_width = 0.5,
                    colorbar_title = 'Goals scored')
        bars = go.Bar(x=top5_x, y=top5_y,
                      orientation='h',
                      marker={
                        'color': top5_x,
                        'colorscale': self.colorscale.text,
                        'reversescale': self.reversescale.checked,
                        'cmin': min(nums),
                        'cmax': max(nums),
        })
        
        self.plot_map.data = map
        self.plot_map.layout.geo = {'showframe': False, 'showcoastlines': False, 'projection_type': 'equirectangular'}
        self.plot_map.layout.title = 'Total amount of goals scored per country'
        
        self.plot_bar.data = bars
        self.plot_bar.layout.title = 'Top 5'

    def form_show(self, **event_args):
        self.call_js('hideSidebar')
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
            self.checkbox_multiselect.enabled = False
            self.timer.interval = 1
            self.button_play.icon = 'fa:pause'
            self.checkbox_multiselect.tooltip = 'Not available during animation'
        else:
            self.timer.interval = 0
            self.button_play.icon = 'fa:play'
            self.checkbox_multiselect.enabled = True
            self.checkbox_multiselect.tooltip = ''

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
            self.button_play.enabled = False
            self.slider_multi.values = [self.slider_single.value, min(2022, self.slider_single.value+4)]
            self.slider_single.visible = False
            self.slider_multi.visible = True
            self.button_play.tooltip = 'Not available in multi-select mode'
        else:
            self.slider_single.value = self.slider_multi.value
            self.slider_multi.visible = False
            self.slider_single.visible = True
            self.button_play.enabled = True
            self.button_play.tooltip = ''
        self.slider_single_change(None)

    def debug_setting_change(self, **event_args):
        self.refresh_data_bindings()
        self.refresh_map()

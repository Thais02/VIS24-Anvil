from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import plotly.graph_objects as go

from collections import Counter

class Form1(Form1Template):
    def __init__(self, **properties):
        self.data = {}
        self.general_data = {}
        self.cmin = 99999
        self.cmax = -99999
        self.custom_cmin_cmax = False
        self.config = {
            'colorscale': 'Reds',
            'reversescale': False,
            'colorbar_title': 'Goals scored',
            'plot_map_layout_title': 'Total amount of goals scored per country',
            'plot_bar_layout_title': 'Top 5'
        }
        self.init_components(**properties)

    def get_data(self):
        self.call_js('hideSidebar')
        self.slider_single.enabled = False
        self.checkbox_multiselect.enabled = False
        self.button_play.enabled = False
        with Notification('Fetching data...', title='Please wait'):
            try:
                anvil.server.call('ping_uplink')
            except:
                self.data, config, self.general_data = anvil.server.call('get_data', vis_name=self.radio_goals.get_group_value())
            else:
                self.data, config, self.general_data = anvil.server.call('get_data_uplink', vis_name=self.radio_goals.get_group_value())
                Notification('Retrieved data from connected local source', title='Data fetched', style='success', timeout=6).show()
            if config:
                self.config = config
            self.reset_cmin_cmax()
        self.slider_single.enabled = True
        self.checkbox_multiselect.enabled = True
        self.button_play.enabled = True
        self.refresh_data_bindings()
        self.refresh_map()

    def reset_cmin_cmax(self):
        self.cmin = 99999
        self.cmax = -99999
        for isos, nums, countries, top5 in self.data.values():
                self.cmin = min(self.cmin, min(nums))
                self.cmax = max(self.cmax, max(nums))
    
    def refresh_map(self):
        self.refresh_data_bindings()
        self.plot_bar.height = 300
        if self.checkbox_multiselect.checked:
            if self.dropdown_multiselect.selected_value == 'show average':
                if self.custom_cmin_cmax:
                    self.reset_cmin_cmax()
                data = {}
                general_data = {}
                iso_to_name = {}
                for year in range(int(self.slider_multi.values[0]), int(self.slider_multi.values[1])+1, 4):
                    if year not in [1942, 1946]:
                        isos, nums, countries, _ = self.data[str(year)]
                        for iso, num, country in zip(isos, nums, countries):
                            lst = data.get(iso, [])
                            lst.append(num)
                            data[iso] = lst
                            iso_to_name[iso] = country
                        for key, value in self.general_data.get(str(year), {}).items():
                            if key in ['Teams', 'Attendance', 'AttendanceAvg', 'Matches']:
                                lst = general_data.get(key, [])
                                lst.append(value)
                                general_data[key] = lst
                isos = list(data.keys())
                nums = [sum(val)/len(val) for val in data.values()]
                countries = [iso_to_name[iso] for iso in data.keys()]
                top5 = {}
                for iso, num in Counter({iso: num for iso, num in zip(isos, nums)}).most_common(5):
                    top5[iso_to_name[iso]] = num
                self.rich_text_side.content = '|  |  |\n| --- | ---: |\n'
                for key, value in general_data.items():
                    self.rich_text_side.content += f'| **{key}** | {int(sum(value)/len(value))} |\n'
            elif self.dropdown_multiselect.selected_value == 'show difference':
                iso_to_name = {}
                isos = []
                nums = []
                countries = []
                isos1, nums1, countries1, _ = self.data[str(int(self.slider_multi.values[0]))]
                isos2, nums2, countries2, _ = self.data[str(int(self.slider_multi.values[1]))]
                for iso, num, country in zip(isos1, nums1, countries1):
                    isos.append(iso)
                    countries.append(country)
                    diff = nums2[isos2.index(iso)] - num
                    nums.append(diff)
                    iso_to_name[iso] = country
                self.cmin = min(nums)
                self.cmax = max(nums)
                self.custom_cmin_cmax = True
                self.plot_bar.height = 400
                top5 = {}
                for iso, num in Counter({iso: num for iso, num in zip(isos, nums)}).most_common(5):
                    top5[iso_to_name[iso]] = num
                for iso, num in Counter({iso: num for iso, num in zip(isos, nums)}).most_common()[-5:]:
                    top5[iso_to_name[iso]] = num
                self.rich_text_side.content = '|  |  |\n| --- | ---: |\n'
                for (key, value1), (_, value2) in zip(self.general_data.get(str(int(self.slider_multi.values[0])), {}).items(),
                                     self.general_data.get(str(int(self.slider_multi.values[1])), {}).items()):
                    if key in ['Teams', 'Attendance', 'AttendanceAvg', 'Matches']:
                        diff = value2 - value1
                        self.rich_text_side.content += f'| {"🔼 " if diff > 0 else "◀️ " if diff == 0 else "🔽 "}**{key}** | {"+" if diff >= 0 else ""}{diff} |\n'
        else:
            if self.custom_cmin_cmax:
                self.reset_cmin_cmax()
            isos, nums, countries, top5 = self.data[str(int(self.slider_single.value))]
            self.rich_text_side.content = '|  |  |\n| --- | ---: |\n'
            for key, value in self.general_data.get(str(int(self.slider_single.value)), {}).items():
                self.rich_text_side.content += f'| **{key}** | {value} |\n'
        
        top5_x = list(top5.values())
        top5_x.reverse()
        top5_y = list(top5.keys())
        top5_y.reverse()

        customdata = []
        for num in nums:
            if num >= 0 and self.dropdown_multiselect.selected_value == 'show difference':
                customdata.append(f'+{num}')
            else:
                customdata.append(num)
        
        map = go.Choropleth(locations=isos, z=nums, text=countries, customdata=customdata,
                    colorscale = self.config.get('colorscale', 'Reds'),
                    hovertemplate='%{customdata}<extra>%{text}</extra>',
                    autocolorscale = False,
                    reversescale = self.config.get('reversescale', False),
                    marker_line_color = 'darkgray',
                    marker_line_width = 0.5,
                    zmin = self.cmin,
                    zmax = self.cmax,
                    colorbar_title = self.config.get('colorbar_title'))
        bars = go.Bar(x=top5_x, y=top5_y,
                      orientation='h',
                      marker={
                        'color': top5_x,
                        'colorscale': self.config.get('colorscale', 'Reds'),
                        'reversescale': self.config.get('reversescale', False),
                        'cmin': self.cmin,
                        'cmax': self.cmax,
        })
        
        self.plot_map.layout.geo = {'showframe': True, 'showcoastlines': False, 'projection_type': 'mercator'}
        self.plot_map.layout.title = self.config.get('plot_map_layout_title', '[untitled]')
        if self.checkbox_multiselect.checked and self.dropdown_multiselect.selected_value == 'show average':
            self.plot_map.layout.title += f'<br>Average between {self.slider_multi.values[0]} and {self.slider_multi.values[1]}'
        elif self.checkbox_multiselect.checked and self.dropdown_multiselect.selected_value == 'show difference':
            self.plot_map.layout.title += f'<br>Difference between {self.slider_multi.values[0]} and {self.slider_multi.values[1]}'
        self.plot_map.data = map
        
        
        self.plot_bar.layout.title = self.config.get('plot_bar_layout_title', '[untitled]')
        self.plot_bar.layout.xaxis.range = [self.cmin, self.cmax]
        self.plot_bar.data = bars
        
    
    def form_show(self, **event_args):
        self.call_js('hideSidebar')
        self.get_data()

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
        self.refresh_map()

    def checkbox_multiselect_change(self, **event_args):
        if self.checkbox_multiselect.checked:
            self.button_play.enabled = False
            self.slider_multi.values = [self.slider_single.value, min(2022, self.slider_single.value+4)]
            self.slider_single.visible = False
            self.slider_multi.visible = True
            self.dropdown_multiselect.enabled = True
            self.button_play.tooltip = 'Not available in multi-select mode'
        else:
            self.slider_single.value = self.slider_multi.value
            self.slider_multi.visible = False
            self.slider_single.visible = True
            self.button_play.enabled = True
            self.dropdown_multiselect.enabled = False
            self.button_play.tooltip = ''
        self.slider_single_change(None)

    def dropdown_multiselect_change(self, **event_args):
        self.slider_single_change(None)

    def debug_setting_change(self, **event_args):
        self.refresh_map()

    def radio_change(self, **event_args):
        self.get_data()

    def plot_map_click(self, points, **event_args):
        print(points)
        isos, _, _, _ = self.data['1930']
        print(isos[int(points[0]['point_number'])])

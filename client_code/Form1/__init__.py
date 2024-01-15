from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import plotly.graph_objects as go

from collections import Counter

continents = {'World': [], None: [], '{custom selection}': [],
        	  'North America': ['ABW', 'AIA', 'ATG', 'BES', 'BHS', 'BLM', 'BLZ', 'BMU', 'BRB', 'CAN', 'CRI', 'CUB', 'CUW', 'CYM', 'DMA', 'DOM', 'GLP', 'GRD', 'GRL', 'GTM', 'HND', 'HTI', 'JAM', 'KNA', 'LCA', 'MAF', 'MEX', 'MSR', 'MTQ', 'NIC', 'PAN', 'PRI', 'SLV', 'SPM', 'TCA', 'TTO', 'USA', 'VCT', 'VGB', 'VIR'],
              'Asia': ['AFG', 'ARE', 'ARM', 'AZE', 'BGD', 'BHR', 'BRN', 'BTN', 'CCK', 'CHN', 'CXR', 'CYP', 'GEO', 'HKG', 'IDN', 'IND', 'IOT', 'IRN', 'IRQ', 'ISR', 'JOR', 'JPN', 'KAZ', 'KGZ', 'KHM', 'KOR', 'KWT', 'LAO', 'LBN', 'LKA', 'MAC', 'MDV', 'MMR', 'MNG', 'MYS', 'NPL', 'OMN', 'PAK', 'PHL', 'PRK', 'PSE', 'QAT', 'SAU', 'SGP', 'SYR', 'THA', 'TJK', 'TKM', 'TUR', 'TWN', 'UZB', 'VNM', 'YEM'],
              'Africa': ['AGO', 'BDI', 'BEN', 'BFA', 'BWA', 'CAF', 'CIV', 'CMR', 'COD', 'COG', 'COM', 'CPV', 'DJI', 'DZA', 'EGY', 'ERI', 'ETH', 'GAB', 'GHA', 'GIN', 'GMB', 'GNB', 'GNQ', 'KEN', 'LBR', 'LBY', 'LSO', 'MAR', 'MDG', 'MLI', 'MOZ', 'MRT', 'MUS', 'MWI', 'MYT', 'NAM', 'NER', 'NGA', 'REU', 'RWA', 'SDN', 'SEN', 'SHN', 'SLE', 'SOM', 'SSD', 'STP', 'SWZ', 'SYC', 'TCD', 'TGO', 'TUN', 'TZA', 'UGA', 'ZAF', 'ZMB', 'ZWE'],
              'Europe': ['ALA', 'ALB', 'AND', 'AUT', 'BEL', 'BGR', 'BIH', 'BLR', 'CHE', 'CZE', 'DEU', 'DNK', 'ESP', 'EST', 'FIN', 'FRA', 'FRO', 'GBR', 'GGY', 'GIB', 'GRC', 'HRV', 'HUN', 'IMN', 'IRL', 'ISL', 'ITA', 'JEY', 'LIE', 'LTU', 'LUX', 'LVA', 'MCO', 'MDA', 'MKD', 'MLT', 'MNE', 'NLD', 'NOR', 'POL', 'PRT', 'ROU', 'RUS', 'SJM', 'SMR', 'SRB', 'SVK', 'SVN', 'SWE', 'UKR'],
              'South America': ['ARG', 'BOL', 'BRA', 'CHL', 'COL', 'ECU', 'FLK', 'GUF', 'GUY', 'PER', 'PRY', 'SGS', 'SUR', 'URY', 'VEN'],
              'Oceania': ['ASM', 'AUS', 'COK', 'FJI', 'FSM', 'GUM', 'KIR', 'MHL', 'MNP', 'NCL', 'NFK', 'NIU', 'NRU', 'NZL', 'PLW', 'PNG', 'PYF', 'SLB', 'TKL', 'TON', 'TUV', 'VUT', 'WLF', 'WSM']}


class Form1(Form1Template):
    def __init__(self, **properties):
        self.data = {}
        self.general_data = {}
        self.cmin = 99999
        self.cmax = -99999
        self.custom_cmin_cmax = False
        self.prev_richtext = ''
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
                self.data, config, self.general_data, self.country_stats = anvil.server.call('get_data', vis_name=self.radio_goals.get_group_value())
            else:
                self.data, config, self.general_data, self.country_stats = anvil.server.call('get_data_uplink', vis_name=self.radio_goals.get_group_value())
                Notification('Retrieved data from connected local source', title='Data fetched', style='success', timeout=6).show()
            if config:
                self.config = config
            self.reset_cmin_cmax()
        self.slider_single.enabled = True
        self.checkbox_multiselect.enabled = True
        self.button_play.enabled = True
        self.plot_map.layout.uirevision = True
        self.plot_map.layout.selectionrevision = True
        self.plot_map.layout.editrevision = True
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
                selected = []
                general_data = {}
                iso_to_name = {}
                year_range = range(int(self.slider_multi.values[0]), int(self.slider_multi.values[1])+1, 4)
                for year in year_range:
                    if year not in [1942, 1946]:
                        isos, nums, countries, _ = self.data[str(year)]
                        for index, (iso, num, country) in enumerate(zip(isos, nums, countries)):
                            lst = data.get(iso, [])
                            lst.append(num)
                            data[iso] = lst
                            iso_to_name[iso] = country
                            if iso in continents.get(self.dropdown_continent.selected_value):
                                selected.append(index)
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
                year_range = list(year_range)
                self.rich_text_side.content = f'|FIFA World Cup|{year_range[0]} - {year_range[-1]}|\n| --- | ---: |\n'
                for key, value in general_data.items():
                    self.rich_text_side.content += f'| **{key}** | {int(sum(value)/len(value))} |\n'
            elif self.dropdown_multiselect.selected_value == 'show difference':
                iso_to_name = {}
                isos = []
                nums = []
                countries = []
                isos1, nums1, countries1, _ = self.data[str(int(self.slider_multi.values[0]))]
                isos2, nums2, countries2, _ = self.data[str(int(self.slider_multi.values[1]))]
                selected = []
                for iso, num, country in zip(isos1, nums1, countries1):
                    isos.append(iso)
                    countries.append(country)
                    diff = nums2[isos2.index(iso)] - num
                    nums.append(diff)
                    iso_to_name[iso] = country
                    if iso in continents.get(self.dropdown_continent.selected_value):
                        selected.append(index)
                self.cmin = min(nums)
                self.cmax = max(nums)
                self.custom_cmin_cmax = True
                self.plot_bar.height = 400
                top5 = {}
                for iso, num in Counter({iso: num for iso, num in zip(isos, nums)}).most_common(5):
                    top5[iso_to_name[iso]] = num
                for iso, num in Counter({iso: num for iso, num in zip(isos, nums)}).most_common()[-5:]:
                    top5[iso_to_name[iso]] = num
                self.rich_text_side.content = f'|FIFA World Cup|{int(self.slider_multi.values[0])} - {int(self.slider_multi.values[1])}|\n| --- | ---: |\n'
                for (key, value1), (_, value2) in zip(self.general_data.get(str(int(self.slider_multi.values[0])), {}).items(),
                                     self.general_data.get(str(int(self.slider_multi.values[1])), {}).items()):
                    if key in ['Teams', 'Attendance', 'AttendanceAvg', 'Matches']:
                        diff = value2 - value1
                        self.rich_text_side.content += f'| {"🔼 " if diff > 0 else "◀️ " if diff == 0 else "🔽 "}**{key}** | {"+" if diff >= 0 else ""}{diff} |\n'
        else:
            if self.custom_cmin_cmax:
                self.reset_cmin_cmax()
            isos, nums, countries, top5 = self.data[str(int(self.slider_single.value))]
            selected = []
            for index, iso in enumerate(isos):
                if iso in continents.get(self.dropdown_continent.selected_value):
                    selected.append(index)
            self.rich_text_side.content = f'|FIFA World Cup|{int(self.slider_single.value)}|\n| --- | ---: |\n'
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
                    selectedpoints = selected if selected else False,
                    uid=420, uirevision=True,
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

    def plot_map_hover(self, points, **event_args):
        index = points[0]['point_number']
        year = int(self.slider_multi.value) if self.checkbox_multiselect.checked else int(self.slider_single.value)
        
        self.prev_richtext = self.rich_text_side.content
        
        isos, nums, countries, _ = self.data[str(year)]
            
        self.rich_text_side.content = f'|{countries[index]}|{year}|\n| --- | ---: |\n'
        for key, value in self.country_stats[str(year)][isos[index]].items():
            self.rich_text_side.content += f'| **{key}** | {value} |\n'

    def plot_map_unhover(self, points, **event_args):
        self.rich_text_side.content = self.prev_richtext

    def plot_map_select(self, points, **event_args):
        year = int(self.slider_multi.value) if self.checkbox_multiselect.checked else int(self.slider_single.value)
        isos, nums, countries, _ = self.data[str(year)]

        indices = [point['point_number'] for point in points]
        selected_isos = [isos[index] for index in indices]
        if selected_isos:
            continents['{custom selection}'] = selected_isos
            self.dropdown_continent.selected_value = '{custom selection}'

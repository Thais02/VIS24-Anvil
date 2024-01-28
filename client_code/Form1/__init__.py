from ._anvil_designer import Form1Template
from anvil import *
import anvil.server

from ..Form2 import Form2
from ..get_data import get_data, get_static_data
from ..drawing import refresh_map

import plotly.graph_objects as go  # Plotly plotting library for interactive plots

from collections import Counter

continents = {'World': [], '{custom selection}': [],
        	  'North America': ['ABW', 'AIA', 'ATG', 'BES', 'BHS', 'BLM', 'BLZ', 'BMU', 'BRB', 'CAN', 'CRI', 'CUB', 'CUW', 'CYM', 'DMA', 'DOM', 'GLP', 'GRD', 'GRL', 'GTM', 'HND', 'HTI', 'JAM', 'KNA', 'LCA', 'MAF', 'MEX', 'MSR', 'MTQ', 'NIC', 'PAN', 'PRI', 'SLV', 'SPM', 'TCA', 'TTO', 'USA', 'VCT', 'VGB', 'VIR'],
              'Asia': ['AFG', 'ARE', 'ARM', 'AZE', 'BGD', 'BHR', 'BRN', 'BTN', 'CCK', 'CHN', 'CXR', 'CYP', 'GEO', 'HKG', 'IDN', 'IND', 'IOT', 'IRN', 'IRQ', 'ISR', 'JOR', 'JPN', 'KAZ', 'KGZ', 'KHM', 'KOR', 'KWT', 'LAO', 'LBN', 'LKA', 'MAC', 'MDV', 'MMR', 'MNG', 'MYS', 'NPL', 'OMN', 'PAK', 'PHL', 'PRK', 'PSE', 'QAT', 'SAU', 'SGP', 'SYR', 'THA', 'TJK', 'TKM', 'TUR', 'TWN', 'UZB', 'VNM', 'YEM'],
              'Africa': ['AGO', 'BDI', 'BEN', 'BFA', 'BWA', 'CAF', 'CIV', 'CMR', 'COD', 'COG', 'COM', 'CPV', 'DJI', 'DZA', 'EGY', 'ERI', 'ETH', 'GAB', 'GHA', 'GIN', 'GMB', 'GNB', 'GNQ', 'KEN', 'LBR', 'LBY', 'LSO', 'MAR', 'MDG', 'MLI', 'MOZ', 'MRT', 'MUS', 'MWI', 'MYT', 'NAM', 'NER', 'NGA', 'REU', 'RWA', 'SDN', 'SEN', 'SHN', 'SLE', 'SOM', 'SSD', 'STP', 'SWZ', 'SYC', 'TCD', 'TGO', 'TUN', 'TZA', 'UGA', 'ZAF', 'ZMB', 'ZWE'],
              'Europe': ['ALA', 'ALB', 'AND', 'AUT', 'BEL', 'BGR', 'BIH', 'BLR', 'CHE', 'CZE', 'DEU', 'DNK', 'ESP', 'EST', 'FIN', 'FRA', 'FRO', 'GBR', 'GGY', 'GIB', 'GRC', 'HRV', 'HUN', 'IMN', 'IRL', 'ISL', 'ITA', 'JEY', 'LIE', 'LTU', 'LUX', 'LVA', 'MCO', 'MDA', 'MKD', 'MLT', 'MNE', 'NLD', 'NOR', 'POL', 'PRT', 'ROU', 'RUS', 'SJM', 'SMR', 'SRB', 'SVK', 'SVN', 'SWE', 'UKR'],
              'South America': ['ARG', 'BOL', 'BRA', 'CHL', 'COL', 'ECU', 'FLK', 'GUF', 'GUY', 'PER', 'PRY', 'SGS', 'SUR', 'URY', 'VEN'],
              'Oceania': ['ASM', 'AUS', 'COK', 'FJI', 'FSM', 'GUM', 'KIR', 'MHL', 'MNP', 'NCL', 'NFK', 'NIU', 'NRU', 'NZL', 'PLW', 'PNG', 'PYF', 'SLB', 'TKL', 'TON', 'TUV', 'VUT', 'WLF', 'WSM']}

continents_coordinates = {
    'World': {'lat': 0, 'lon': 0, 'scale': 1}, '{custom selection}': {'lat': 0, 'lon': 0, 'scale': 1},
    'North America': {'lat': 50, 'lon': -100, 'scale': 1.8},
    'Asia': {'lat': 35, 'lon': 90, 'scale': 1.8},
    'Africa': {'lat': 5, 'lon': 25, 'scale': 2},
    'Europe': {'lat': 50, 'lon': 15, 'scale': 2.5},
    'South America': {'lat': -15, 'lon': -60, 'scale': 2},
    'Oceania': {'lat': -10, 'lon': 130, 'scale': 1.8},
}

class Form1(Form1Template):
    def __init__(self, **properties):
        self.vises = {}
        self.data = {}
        self.general_data = {}
        self.country_stats, self.country_stats_ext = {}, {}
        self.cards_per_country = {}
        self.multivariate = {}
        self.form2 = None
        self.cmin = 99999
        self.cmax = -99999
        self.custom_cmin_cmax = False
        self.prev_richtext = ''
        self.config = {
            'colorscale': 'Reds',
            'reversescale': False,
            'colorbar_title': 'Goals',
            'plot_map_layout_title': 'Total amount of goals scored per country',
            'plot_bar_layout_title': 'Top 5'
        }
        self.init_components(**properties)

    def form_show(self, **event_args):
        get_static_data(form=self)
        get_data(form=self, noti=not self.label_uplink.visible)
        self.refresh_map()    

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
        self.config['colorscale'] = self.dropdown_colorscale.selected_value
        self.refresh_map()

    def radio_change(self, **event_args):
        self.form2 = None
        self.column_panel_1.clear()
        self.up_button.visible = False
        get_data(form=self)
        val = self.radio_xg.get_group_value()
        if val in ['xg', 'xp']:
            self.card_sliders.visible = True
            self.panel_settings.visible = True
            self.card_sideplot1.visible = True
            self.card_sideplot2.visible = True
            self.cards_map_sides.visible = True
            self.button_play.enabled = False
            self.slider_multi.values = [2018, 2022]
            self.slider_single.visible = False
            self.slider_multi.visible = True
            self.slider_multi.enabled = False
            self.checkbox_multiselect.enabled = False
            self.checkbox_multiselect.checked = True
            self.dropdown_multiselect.enabled = False
            self.dropdown_multiselect.selected_value = 'show average'
            self.button_play.tooltip = 'Not available for this visualization'
            self.hint_multiselect.visible = True
        elif val == 'cards':
            self.card_sideplot1.visible = False
            self.card_sideplot2.visible = False
            self.card_sliders.visible = False
            self.panel_settings.visible = False
            self.hint_maptap.visible = False
        elif val == 'pos':
            self.card_sliders.visible = True
            self.panel_settings.visible = True
            self.card_sideplot1.visible = True
            self.card_sideplot2.visible = True
            self.slider_multi.enabled = True
            self.card_sideplot1.visible = False
            self.checkbox_multiselect.enabled = False
            self.checkbox_multiselect.checked = False
            self.dropdown_multiselect.enabled = False
            self.slider_single.visible = True
            self.slider_multi.visible = False
            self.button_play.enabled = True
            self.button_play.tooltip = ''
            self.hint_multiselect.visible = False
        else:
            self.card_sliders.visible = True
            self.panel_settings.visible = True
            self.card_sideplot1.visible = True
            self.card_sideplot2.visible = True
            self.slider_multi.enabled = True
            self.checkbox_multiselect.enabled = True
            self.hint_multiselect.visible = False
        self.refresh_map()

    def plot_map_hover(self, points, **event_args):
        if self.radio_xg.get_group_value() != 'cards':
            index = points[0]['point_number']
            year = int(self.slider_multi.value) if self.checkbox_multiselect.checked else int(self.slider_single.value)
            
            self.prev_richtext = self.rich_text_side.content
            
            isos, nums, countries, _ = self.data[str(year)]
    
            try:
                self.rich_text_side.content = f'|{countries[index]}|{year}|\n| --- | ---: |\n'
                for key, value in self.country_stats[str(year)][isos[index]].items():
                    self.rich_text_side.content += f'| **{key}** | {value} |\n'
            except:
                pass

    def plot_map_unhover(self, points, **event_args):
        if self.radio_xg.get_group_value() != 'cards':
            self.rich_text_side.content = self.prev_richtext

    def plot_map_select(self, points, **event_args):
        if self.radio_xg.get_group_value() != 'cards':
            year = int(self.slider_multi.value) if self.checkbox_multiselect.checked else int(self.slider_single.value)
            isos, nums, countries, _ = self.data[str(year)]
    
            indices = [point['point_number'] for point in points]
            selected_isos = [isos[index] for index in indices]
            if selected_isos:
                continents['{custom selection}'] = selected_isos
                self.dropdown_continent.selected_value = '{custom selection}'

    def plot_map_click(self, points, **event_args):
        if self.radio_xg.get_group_value() != 'cards':
            index = points[0]['point_number']
            year = int(self.slider_multi.value) if self.checkbox_multiselect.checked else int(self.slider_single.value)
            
            isos, nums, countries, _ = self.data[str(year)]
    
            iso = isos[index]
            country = countries[index]

            year = self.slider_multi.values if self.checkbox_multiselect.checked else int(self.slider_single.value)
            
            self.form2 = Form2(self.country_stats_ext.get(iso, []), self.cards_per_country.get(iso, ([], [], [])), self.multivariate.get(iso, {}),
                               year=year, country=country)
    
            self.column_panel_1.clear()
            self.column_panel_1.add_component(self.form2, full_width_row=True)
            self.column_panel_1.scroll_into_view(smooth=True)
            
            self.up_button.visible = True
            self.hint_maptap.visible = False

    def up_button_click(self, **event_args):
        self.cards_map_sides.scroll_into_view(smooth=True)

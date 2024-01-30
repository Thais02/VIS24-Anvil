# import framework stuff
from ._anvil_designer import homeTemplate
from anvil import *
from anvil_extras import popover  # library which provides the small pop-up for the visualization hints

from ..country_form import country_form  # multivariate scatterplot, cards per country, extended country stats
from ..get_data import get_data, get_static_data  # fetches data from (local) server
from ..drawing import refresh_map, colorscales  # actual plotting functions

hints = {
    'pos': ['Highest round reached', "This map shows which country has reached which round of that year's World Cup"],
    'goals': ['Goals per year', "This map shows how many total goals each participating country has scored that year"],
    'xg': ['Expected goals', "This map shows how much more/less goals each country scored compared to the expected number of goals that were predicted"],
    'xp': ['Expected winrate',
           "This map shows how countries performed relative to the expectation. A relative winrate of 100% means a country won all matches they were expected to lose, and did not lose any matches they were expected to win. -100% means the exact opposite"],
}

class home(homeTemplate):
    def __init__(self, **properties):
        # runs before the page loads
        self.vises = {}
        self.data = {}
        self.general_data = {}
        self.country_stats, self.country_stats_ext = {}, {}
        self.cards_per_country = {}
        self.multivariate = {}
        self.country_form = None
        self.cmin = 99999
        self.cmax = -99999
        self.custom_cmin_cmax = False
        self.prev_richtext = ''
        self.config = {
            'colorscale': 'Blues',
            'reversescale': True,
            'colorbar_title': 'Goals',
            'plot_map_layout_title': 'Total amount of goals scored per country',
            'plot_bar_layout_title': 'Top 5'
        }
        self.init_components(**properties)
        self.dropdown_colorscale.items = colorscales['seq']
        self.set_hint_popover('pos')

    def form_show(self, **event_args):
        # Runs once as soon as the page is loaded, fetches startup data and first visualization data
        get_static_data(form=self)
        get_data(form=self, noti=not self.label_uplink.visible)
        refresh_map(form=self)

    def reset_cmin_cmax(self):
        # Calculates the max and min values present over all years, to sync the colorbar over all years
        self.cmin = 99999
        self.cmax = -99999
        for isos, nums, countries, top5 in self.data.values():
            self.cmin = min(self.cmin, min(nums))
            self.cmax = max(self.cmax, max(nums))

    def set_hint_popover(self, vis_name):
        # Sets the pop-up on the "get more visualization info" button
        if popover.has_popover(self.hint_popover):
            popover.pop(self.hint_popover, 'destroy')
        popover.popover(self.hint_popover, hints.get(vis_name, ['Unavailable', 'No info available'])[1], title=hints.get(vis_name, ['Unavailable'])[0],
                        trigger='hover click', placement='top', auto_dismiss=True, animation=True)
        self.hint_popover.visible = True

    def button_play_click(self, **event_args):
        # Handles playing/pausing the year animation
        if self.button_play.icon == 'fa:play':
            self.checkbox_multiselect.enabled = False
            self.timer.interval = 1
            self.button_play.icon = 'fa:pause'
            self.checkbox_multiselect.tooltip = 'Not available during animation'
        else:
            self.timer.interval = 0
            self.button_play.icon = 'fa:play'
            self.checkbox_multiselect.enabled = self.radio_xg.get_group_value() != 'pos'
            self.checkbox_multiselect.tooltip = 'Not available for this visualization' if self.radio_xg.get_group_value() != 'pos' else ''

    def timer_tick(self, **event_args):
        # If the year animation is playing, each tick (1 second) move the slider 4 years forward and set the visualization
        if self.slider_single.value + 4 == 1942 or self.slider_single.value + 4 == 1946:
            self.slider_single.value = 1950
        elif self.slider_single.value + 4 > 2022:
            self.slider_single.value = 1930
        else:
            self.slider_single.value += 4
        refresh_map(self)

    def checkbox_multiselect_change(self, **event_args):
        # Add/remove an additional handle to the year slider
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
        refresh_map(self)

    def setting_change(self, **event_args):
        # If any setting has changed, redraw the visualizations
        refresh_map(self)

    def radio_change(self, **event_args):
        # When another visualization is selected, set all corresponding visualization-specific settings
        self.country_form = None
        self.column_panel_1.clear()
        self.up_button.visible = False
        get_data(form=self)
        val = self.radio_xg.get_group_value()
        self.set_hint_popover(val)
        if val in ['xg', 'xp']:
            self.card_sliders.visible = True
            self.panel_settings.visible = True
            self.card_sideplot1.visible = True
            self.card_sideplot2.visible = True
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
            self.dropdown_colorscale.items = colorscales['div']
            self.config['colorscale'] = 'RdBu'
            self.card_colourscale.visible = True
        elif val == 'cards':
            self.card_sideplot1.visible = False
            self.card_sideplot2.visible = False
            self.card_sliders.visible = False
            self.panel_settings.visible = False
            self.hint_maptap.visible = False
            self.hint_popover.visible = False
            self.dropdown_colorscale.items = colorscales['seq']
            self.config['colorscale'] = 'Blues'
            self.card_colourscale.visible = True
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
            self.card_colourscale.visible = False
            self.dropdown_colorscale.items = colorscales['seq']
            self.config['colorscale'] = 'Blues'
        else:  # only the 'goals' visualization
            self.card_sliders.visible = True
            self.panel_settings.visible = True
            self.card_sideplot1.visible = True
            self.card_sideplot2.visible = True
            self.slider_multi.enabled = True
            self.checkbox_multiselect.enabled = True
            self.hint_multiselect.visible = False
            self.dropdown_colorscale.items = colorscales['seq']
            self.config['colorscale'] = 'Blues'
            self.card_colourscale.visible = True
        self.refresh_data_bindings()
        refresh_map(self)

    def plot_map_hover(self, points, **event_args):
        # When hovering over a country, display country-specific stats in the sidebar
        if self.radio_xg.get_group_value() != 'cards':
            index = points[0]['point_number']
            year = int(self.slider_multi.value) if self.checkbox_multiselect.checked else int(self.slider_single.value)
            
            self.prev_richtext = self.rich_text_side.content

            if self.radio_xg.get_group_value() == 'pos':
                seen = 0
                for i_r in range(6, -1, -1):
                    if self.data[2][str(year)][str(i_r)]:
                        if seen == points[0]['curve_number']:
                            iso_tuples = self.data[2][str(year)][str(i_r)]
                            iso, name = iso_tuples[index]
                            break
                        seen += 1
            else:
                isos, _, countries, _ = self.data[str(year)]
                iso = isos[index]
                name = countries[index]
            
            try:
                self.rich_text_side.content = f'|{name}|{year}|\n| --- | ---: |\n'
                for key, value in self.country_stats[str(year)][iso].items():
                    self.rich_text_side.content += f'| **{key}** | {value} |\n'
            except:
                pass

    def plot_map_unhover(self, points, **event_args):
        # Reset the general statistics in the sidebar when a country is no longer hovered over
        if self.radio_xg.get_group_value() != 'cards':
            self.rich_text_side.content = self.prev_richtext

    def plot_map_select(self, points, **event_args):
        # When drawing a selection, remember these countries to also select them when redrawing
        if self.radio_xg.get_group_value() != 'cards':
            year = int(self.slider_multi.value) if self.checkbox_multiselect.checked else int(self.slider_single.value)
            
            if self.radio_xg.get_group_value() == 'pos':
                selected_isos = []
                for point in points:
                    seen = 0
                    for i_r in range(6, -1, -1):
                        if self.data[2][str(year)][str(i_r)]:
                            if seen == point['curve_number']:
                                iso_tuples = self.data[2][str(year)][str(i_r)]
                                iso, name = iso_tuples[index]
                                selected_isos.append(iso)
                                break
                            seen += 1
            else:
                isos, _, countries, _ = self.data[str(year)]
                indices = [point['point_number'] for point in points]
                selected_isos = [isos[index] for index in indices]
    
            if selected_isos:
                continents['{custom selection}'] = selected_isos
                self.dropdown_continent.selected_value = '{custom selection}'

    def plot_map_click(self, points, **event_args):
        # Open the country_form for the clicked country and scroll to it
        if self.radio_xg.get_group_value() != 'cards':
            index = points[0]['point_number']
            year = int(self.slider_multi.value) if self.checkbox_multiselect.checked else int(self.slider_single.value)
            
            if self.radio_xg.get_group_value() == 'pos':
                seen = 0
                for i_r in range(6, -1, -1):
                    if self.data[2][str(year)][str(i_r)]:
                        if seen == points[0]['curve_number']:
                            iso_tuples = self.data[2][str(year)][str(i_r)]
                            iso, name = iso_tuples[index]
                            break
                        seen += 1
            else:
                isos, _, countries, _ = self.data[str(year)]
                iso = isos[index]
                name = countries[index]

            year = self.slider_multi.values if self.checkbox_multiselect.checked else int(self.slider_single.value)
            
            self.country_form = country_form(self.country_stats_ext.get(iso, []), self.cards_per_country.get(iso, ([], [], [])), self.multivariate.get(iso, {}),
                               year=year, country=name)
    
            self.column_panel_1.clear()
            self.column_panel_1.add_component(self.country_form, full_width_row=True)
            self.column_panel_1.scroll_into_view(smooth=True)
            
            self.up_button.visible = True
            self.hint_maptap.visible = False

    def up_button_click(self, **event_args):
        # Scroll back up to the main visualization
        self.cards_map_sides.scroll_into_view(smooth=True)

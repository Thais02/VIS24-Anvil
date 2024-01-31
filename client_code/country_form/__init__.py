from ._anvil_designer import country_formTemplate
from anvil import *
import anvil.server

import plotly.graph_objects as go

from ..drawing import margins_bar

margins_scatter = dict(l=5, r=10, b=0, t=0)

class country_form(country_formTemplate):
    def __init__(self, dic, cards_data, scatter, year, country='', **properties):
        # Runs before the form is displayed
        self.dic = dic
        self.years, self.reds, self.yellows = cards_data
        self.scatter = scatter
        self.country = country
        self.closest_years = {0: [], 1: [], 2: []}  # data_index : [closest_years xaxis-values]
        self.selected = True
        
        self.init_components(**properties)
        self.update(year, full=True)

    def update(self, year, full=False):
        # Redraw the visualizations, only update the selected points of that year
        self.year = year
        
        self.draw_cards_bar(year, full=full)
        self.draw_scatter(year, full=full)

        if full:
            self.richtext_side.content = f'|{self.country}|1930 - 2022|\n| --- | ---: |\n'
            for key, value in self.dic:
                self.richtext_side.content += f'| **{key}** | {value} |\n'

    def draw_cards_bar(self, year, full):
        index = None
        if year:
            if isinstance(year, int):
                try:
                    index = self.years.index(year)
                except ValueError:
                    index = None
            else:
                index = []
                for y in range(year[0], year[1]+1, 4):
                    try:
                        i = self.years.index(y)
                        index.append(i)
                    except ValueError:
                        pass

        selectedpoints = False
        if year and index is not None:
            if isinstance(year, int):
                if self.reds[index] or self.yellows[index]:
                    selectedpoints = [index]
            else:
                for i in index:
                    if self.reds[i] or self.yellows[i]:
                        selectedpoints = index
                        break
            
        if full:
            self.plot.layout = {'barmode': 'stack', 'margin': margins_bar}
            self.plot.layout.xaxis.tick0 = 1930
            self.plot.layout.xaxis.dtick = 4
            self.plot.layout.xaxis.title = 'Year'
            self.plot.layout.yaxis.title = 'Total number of cards'
            self.plot.layout.title = {'text': f"<b>{self.country}</b><br>Red and yellow cards per year", 'x': 0.5}
            
            self.plot.data = [
                go.Bar(name='Red cards', x=self.years, y=self.reds, marker={'color': '#DA291C'}, selectedpoints=selectedpoints),
                go.Bar(name='Yellow cards', x=self.years, y=self.yellows, marker={'color': '#FFC72C'}, selectedpoints=selectedpoints)
            ]
        else:
            for data in self.plot.data:
                if self.checkbox_highlight.checked:
                    data.selectedpoints = selectedpoints
                elif self.selected:
                    data.selectedpoints = False
                else:
                    return
            self.plot.redraw()

    def find_closest_years(self, nums):
        # As the years in the data are jittered, find the year they are closest to to know if we need to select them
        years = range(1930, 2022 + 1, 4)
        res = []
        for num in nums:
            res.append(min(years, key=lambda year: abs(year - num)))
        return res
    
    def draw_scatter(self, year, full):
        if full:
            self.plot_scatter.figure = self.scatter
            self.plot_scatter.layout.margins = margins_scatter
            self.plot_scatter.layout.title = {'text': f'<b>{self.country}</b><br>Match results per year', 'x': 0.5}

        if self.checkbox_highlight.checked:
            made_selection = False
            selected = {0: [], 1: [], 2: []}
            for data_index, data in enumerate(self.plot_scatter.figure.data):
                if not self.closest_years[data_index]:
                    self.closest_years[data_index] = self.find_closest_years(data['x'])
                if isinstance(year, int):
                    for index, closest_year in enumerate(self.closest_years[data_index]):
                        if closest_year == year:
                            selected[data_index].append(index)
                            made_selection = True
                else:
                    years_range = range(year[0], year[1]+1, 4)
                    for index, closest_year in enumerate(self.closest_years[data_index]):
                        if closest_year in years_range:
                            selected[data_index].append(index)
                            made_selection = True
    
        for data_index, data in enumerate(self.plot_scatter.figure.data):
            if self.checkbox_highlight.checked:
                data.selectedpoints = selected[data_index] if selected[data_index] or made_selection else False
            elif self.selected:
                data.selectedpoints = False
            else:
                return
        self.plot_scatter.redraw()

    def close_button_click(self, **event_args):
        # Delete this form from the homepage (parent)
        self.parent.parent.parent.up_button_click()
        self.parent.parent.parent.country_form = None
        self.parent.clear()
        del self

    def checkbox_highlight_change(self, **event_args):
        self.update(self.year)
        if self.checkbox_highlight.checked:
            self.selected = False

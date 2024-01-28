import plotly.graph_objects as go  # Plotly plotting library for interactive plots


def draw_map(form, isos, nums, countries, custom, selected):
    customdata = []
    for index, num in enumerate(nums):
        if num >= 0 and form.dropdown_multiselect.selected_value == 'show difference':
            customdata.append(f'+{num}')
        elif custom:
            customdata.append(custom[index])
        else:
            customdata.append(num)

    map = go.Choropleth(locations=isos, z=nums, text=countries, customdata=customdata,
                    colorscale = form.config.get('colorscale', 'Reds'),
                    hovertemplate='%{customdata}<extra>%{text}</extra>',
                    autocolorscale = False,
                    reversescale = form.config.get('reversescale', False),
                    marker_line_color = 'darkgray',
                    marker_line_width = 0.5,
                    zmin = form.cmin,
                    zmax = form.cmax,
                    selectedpoints = selected if selected else False,
                    colorbar_title = form.config.get('colorbar_title'))

    continent = form.dropdown_continent.selected_value
    form.plot_map.layout.geo = {'showframe': form.checkbox_frame.checked, 'showcoastlines': False, 'showocean': form.checkbox_water.checked,
                                'projection': {'type': form.dropdown_projection.selected_value, 'scale': continents_coordinates[continent]['scale'] if not form.checkbox_scope.checked else 1},
                                'center': {'lat': continents_coordinates[continent]['lat'], 'lon': continents_coordinates[continent]['lon']} if not form.checkbox_scope.checked else {},
                                'scope': continent.lower() if form.checkbox_scope.checked else 'world',
                                'showcountries': True, 'countrywidth': 0.5, 'countrycolor': 'darkgray'
                                }
    form.plot_map.layout.title = form.config.get('plot_map_layout_title', '[untitled]')
    if form.checkbox_multiselect.checked and form.dropdown_multiselect.selected_value == 'show average':
        form.plot_map.layout.title += f'<br>Average between {form.slider_multi.values[0]} and {form.slider_multi.values[1]}'
    elif form.checkbox_multiselect.checked and form.dropdown_multiselect.selected_value == 'show difference':
        form.plot_map.layout.title += f'<br>Difference between {form.slider_multi.values[0]} and {form.slider_multi.values[1]}'
    form.plot_map.data = map

def draw_top5(form, top5):
    try:
        top5_x = list(top5.values())
    except:
        # year is 1942 or 1946
        form.plot_bar.data = []
        return
    top5_x.reverse()
    top5_y = list(top5.keys())
    top5_y.reverse()
    
    bars = go.Bar(x=top5_x, y=top5_y,
                    orientation='h',
                    marker={
                    'color': top5_x,
                    'colorscale': form.config.get('colorscale', 'Reds'),
                    'reversescale': form.config.get('reversescale', False),
                    'cmin': form.cmin,
                    'cmax': form.cmax,
    })
    
    form.plot_bar.layout.title = form.config.get('plot_bar_layout_title', '[untitled]')
    form.plot_bar.layout.xaxis.range = [form.cmin, form.cmax]
    form.plot_bar.data = bars

def draw_cards_corr(form):
    years, reds, yellows = form.data

    form.plot_map.layout = {'barmode': 'stack'}
    form.plot_map.layout.xaxis.tick0 = 1930
    form.plot_map.layout.xaxis.dtick = 4
    form.plot_map.layout.xaxis.title = 'Year'
    form.plot_map.layout.yaxis.title = 'Average number of cards per match'

    form.plot_map.layout.title = "Normalised red and yellow cards per year<br>I'm lovin' it"
    
    form.plot_map.data = [
        go.Bar(name='Red cards', x=years, y=reds, marker={'color': '#DA291C'}),
        go.Bar(name='Yellow cards', x=years, y=yellows, marker={'color': '#FFC72C'})
    ]

def reset_cmin_cmax(form):
    form.cmin = 99999
    form.cmax = -99999
    for isos, nums, countries, top5 in form.data.values():
        form.cmin = min(form.cmin, min(nums))
        form.cmax = max(form.cmax, max(nums))

def refresh_map(form):
    form.plot_bar.height = 300
    if form.radio_xg.get_group_value() in ['xg', 'xp']:
        isos, nums, countries, top5 = form.data['2018']
        form.draw_map(isos, nums, countries, [], False)
        form.draw_top5(top5)
        general_data = {}
        for year in [2018, 2022]:
            for key, value in form.general_data.get(str(year), {}).items():
                if key in ['Teams', 'Attendance', 'AttendanceAvg', 'Matches']:
                    lst = general_data.get(key, [])
                    lst.append(value)
                    general_data[key] = lst
        form.rich_text_side.content = f'|FIFA World Cup|2018 - 2022|\n| --- | ---: |\n'
        for key, value in general_data.items():
            form.rich_text_side.content += f'| **{key}** | {int(sum(value)/len(value))} |\n'
    elif form.radio_xg.get_group_value() == 'cards':
        form.draw_cards_corr()
    elif form.radio_xg.get_group_value() == 'performance':
        pass
    else:
        if form.checkbox_multiselect.checked:
            if form.dropdown_multiselect.selected_value == 'show average':
                if form.custom_cmin_cmax:
                    reset_cmin_cmax(form)
                data = {}
                selected = []
                general_data = {}
                iso_to_name = {}
                year_range = range(int(form.slider_multi.values[0]), int(form.slider_multi.values[1])+1, 4)
                for year in year_range:
                    if year not in [1942, 1946]:
                        isos, nums, countries, _ = form.data[str(year)]
                        for index, (iso, num, country) in enumerate(zip(isos, nums, countries)):
                            lst = data.get(iso, [])
                            lst.append(num)
                            data[iso] = lst
                            iso_to_name[iso] = country
                            if iso in continents.get(form.dropdown_continent.selected_value):
                                selected.append(index)
                        for key, value in form.general_data.get(str(year), {}).items():
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
                form.rich_text_side.content = f'|FIFA World Cup|{year_range[0]} - {year_range[-1]}|\n| --- | ---: |\n'
                for key, value in general_data.items():
                    form.rich_text_side.content += f'| **{key}** | {int(sum(value)/len(value))} |\n'
            elif form.dropdown_multiselect.selected_value == 'show difference':
                iso_to_name = {}
                isos = []
                nums = []
                countries = []
                isos1, nums1, countries1, _ = form.data[str(int(form.slider_multi.values[0]))]
                isos2, nums2, countries2, _ = form.data[str(int(form.slider_multi.values[1]))]
                selected = []
                for iso, num, country in zip(isos1, nums1, countries1):
                    isos.append(iso)
                    countries.append(country)
                    diff = nums2[isos2.index(iso)] - num
                    nums.append(diff)
                    iso_to_name[iso] = country
                    if iso in continents.get(form.dropdown_continent.selected_value):
                        selected.append(index)
                form.cmin = min(nums)
                form.cmax = max(nums)
                form.custom_cmin_cmax = True
                form.plot_bar.height = 400
                top5 = {}
                for iso, num in Counter({iso: num for iso, num in zip(isos, nums)}).most_common(5):
                    top5[iso_to_name[iso]] = num
                for iso, num in Counter({iso: num for iso, num in zip(isos, nums)}).most_common()[-5:]:
                    top5[iso_to_name[iso]] = num
                form.rich_text_side.content = f'|FIFA World Cup|{int(form.slider_multi.values[0])} - {int(form.slider_multi.values[1])}|\n| --- | ---: |\n'
                for (key, value1), (_, value2) in zip(form.general_data.get(str(int(form.slider_multi.values[0])), {}).items(),
                                    form.general_data.get(str(int(form.slider_multi.values[1])), {}).items()):
                    if key in ['Teams', 'Attendance', 'AttendanceAvg', 'Matches']:
                        diff = value2 - value1
                        form.rich_text_side.content += f'| {"🔼 " if diff > 0 else "◀️ " if diff == 0 else "🔽 "}**{key}** | {"+" if diff >= 0 else ""}{diff} |\n'
        else:
            if form.custom_cmin_cmax:
                reset_cmin_cmax(form)
            isos, nums, countries, top5 = form.data[str(int(form.slider_single.value))]
            selected = []
            for index, iso in enumerate(isos):
                if iso in continents.get(form.dropdown_continent.selected_value):
                    selected.append(index)
            form.rich_text_side.content = f'|FIFA World Cup|{int(form.slider_single.value)}|\n| --- | ---: |\n'
            for key, value in form.general_data.get(str(int(form.slider_single.value)), {}).items():
                form.rich_text_side.content += f'| **{key}** | {value} |\n'

        custom = form.data[str(int(form.slider_multi.value) if form.checkbox_multiselect.checked else int(form.slider_single.value))][3] if form.radio_xg.get_group_value() == 'pos' else []
        draw_map(form, isos, nums, countries, custom, selected)
        if form.radio_xg.get_group_value() in ['goals', 'xg', 'xp']:
            draw_top5(form, top5)
        if form.form2:
            form.form2.update(year=form.slider_multi.values if form.checkbox_multiselect.checked else int(form.slider_single.value))

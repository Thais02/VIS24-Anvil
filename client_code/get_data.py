from anvil import Notification
import anvil.server

def get_static_data(form):
    # This data is visualization-independent and only needs to be retrieved once per website visit
    # takes some time because of the multivariate scatterplot plotting in px
    with Notification('Fetching data...\nThis can take up to 15 seconds', title='Please wait'):
        try:
            # check if an uplink is online and give that priority if so
            anvil.server.call('ping_uplink')
            form.label_uplink.visible = True
        except:
            form.label_uplink.visible = False
            form.general_data, form.country_stats_ext, form.cards_per_country, form.multivariate = anvil.server.call('get_static_data')
        else:
            try:
                form.general_data, form.country_stats_ext, form.cards_per_country, form.multivariate = anvil.server.call('get_static_data_uplink')
            except Exception as e:
                Notification(str(e), title='Uplink script threw uncaught exception', style='danger', timeout=0).show()
                form.general_data, form.country_stats_ext, form.cards_per_country, form.multivariate = {}, {}, {}, {}

def _get_vis_data(form, vis_name):  # executed in a `with Notification` block
    org_slider = form.slider_multi.enabled
    org_checkbox = form.checkbox_multiselect.enabled
    org_button = form.button_play.enabled
    form.slider_single.enabled = False
    form.slider_multi.enabled = False
    form.checkbox_multiselect.enabled = False
    form.button_play.enabled = False
    try:
        # check if an uplink is online and give that priority if so
        anvil.server.call('ping_uplink')
        form.label_uplink.visible = True
    except:
        form.label_uplink.visible = False
        data, config, country_stats = anvil.server.call('get_data', vis_name=vis_name)
    else:
        try:
            data, config, country_stats = anvil.server.call('get_data_uplink', vis_name=vis_name)
        except Exception as e:
            Notification(str(e), title='Uplink script threw uncaught exception', style='danger', timeout=0).show()
            data, config, country_stats = {}, form.config, {}
    form.vises[vis_name] = (data, config, country_stats)
    form.data = data
    form.country_stats = country_stats
    if config:
        form.config = config
    if vis_name not in ['pos', 'cards']:
        form.reset_cmin_cmax()
    form.slider_single.enabled = True
    form.slider_multi.enabled = org_slider
    form.checkbox_multiselect.enabled = org_checkbox
    form.button_play.enabled = org_button
    form.refresh_data_bindings()

def get_data(form, noti=True):
    vis_name = form.radio_xg.get_group_value()
    if vis_name in form.vises:  # if we have already retrieved this visualization-data, simply load it from our cache
        data, config, country_stats = form.vises[vis_name]
        form.data = data
        form.country_stats = country_stats
        if config:
            form.config = config
        if vis_name not in ['pos', 'cards']:
            form.reset_cmin_cmax()
        form.refresh_data_bindings()
        return
    org_slider = form.slider_multi.enabled
    org_checkbox = form.checkbox_multiselect.enabled
    org_button = form.button_play.enabled
    form.slider_single.enabled = False
    form.slider_multi.enabled = False
    form.checkbox_multiselect.enabled = False
    form.button_play.enabled = False
    if noti:
        with Notification('Loading visualization...', title='Please wait'):
            _get_vis_data(form, vis_name)
    else:
        _get_vis_data(form, vis_name)
    form.slider_single.enabled = True
    form.slider_multi.enabled = org_slider
    form.checkbox_multiselect.enabled = org_checkbox
    form.button_play.enabled = org_button
    form.refresh_data_bindings()

import pycountry


def get_iso_name(country_name):
    # shorthand function
    iso = get_iso(country_name)
    return iso, get_name(iso)


def get_iso(country_name):
    """Convert a string of a country name to a 3-letter ISO_3166-1_alpha-3 value for the map"""
    isos = {  # list of manually added countries not recognized by pycountry
        'Russia': 'RUS',
        'IR Iran': 'IRN',
        'Korea Republic': 'KOR',  # South korea
        'Korea DPR': 'PRK',  # Best korea
        'Czech Republic': 'CZE',
        'Türkiye': 'TUR',
        'Republic of Ireland': 'IRL',
        'China PR': 'CHN',
        'Bolivia': 'BOL',
        'Zaire': 'COD',  # Democratic Congo
        'Dutch East Indies': 'IDN',  # Indonesia
        # All English teams are combined as Great Britain
        'England': 'GBR',
        'Wales': 'GBR',
        'Scotland': 'GBR',
        'Northern Ireland': 'GBR',
        # Both halves of Germany are combined
        'West Germany': 'DEU',
        'Germany DR': 'DEU',
        # Montenegro is tiny so treat it as just Serbia
        'Serbia and Montenegro': 'SRB',
        # Yugoslavia fell apart into many countries but former capital became Serbia
        'FR Yugoslavia': 'SRB',  # Serbia
        'Yugoslavia': 'SRB',  # Serbia
        # Idem with Czechoslovakia
        'Czechoslovakia': 'CZE',  # Czech Republic
        # Soviet Union football team has been combined with Russia
        'Soviet Union': 'RUS',
    }
    try:
        iso = pycountry.countries.get(name=country_name).alpha_3
    except:
        iso = isos.get(country_name)
    return iso


def get_name(iso):
    try:
        # try common_name first if it exists, else name
        name = pycountry.countries.get(alpha_3=iso).common_name
    except:
        name = pycountry.countries.get(alpha_3=iso).name
    return name

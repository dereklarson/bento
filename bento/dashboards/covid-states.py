from common import logger
from loaddata import nyt
from bento.bento import Bento

logging = logger.fancy_logger(__name__)


def generate(repobase):
    series_page = {
        "banks": {
            "selector": {
                "type": "axis_controls",
                "position": (0, 0),
                "args": {"use": "xy"},
            },
            "proj": {"type": "fit_controls", "position": (0, 4), "args": {}},
            "filterset": {
                "type": "filters",
                "position": (1, 0),
                "args": {"columns": ["state"]},
            },
            "confmap": {"type": "graph", "position": (2, 0), "args": {}},
        },
        "layout": {"width": 12, "height": 8},
        "connections": {
            "selector": {"confmap": ["figure"]},
            "filterset": {"confmap": ["figure"]},
            "proj": {"confmap": ["figure"]},
        },
    }

    map_page = {
        "banks": {
            "selector": {
                "type": "axis_controls",
                "position": (0, 0),
                "args": {"use": "z"},
            },
            "playback": {"type": "date_slider", "position": (6, 0), "args": {}},
            "usmap": {
                "type": "graph",
                "position": (0, 4),
                "args": {
                    "variant": "choropleth",
                    "loc_column": "abbr",
                    "time_column": "date",
                    "locationmode": "USA-states",
                    "scope": "usa",
                },
            },
        },
        "layout": {"width": 12, "height": 8},
        "connections": {
            "selector": {"usmap": ["figure"]},
            "playback": {"usmap": ["figure"]},
        },
    }

    descriptor = {
        "name": "covid",
        "title": "Covid-19 Analysis Dashboard",
        "pages": {"series": series_page, "map": map_page},
        "data": {
            "location": repobase,
            "repos": ["nyt-covid-states"],
            "calls": {"dataname": nyt.load},
        },
    }

    bento = Bento(descriptor)
    return bento

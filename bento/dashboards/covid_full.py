globe_page = {
    "dataid": "covid_world",
    "banks": {
        "agg": {
            "type": "indicators",
            "width": 3,
            "args": {
                "components": [
                    {"args": {"y_column": "cases"}},
                    {"args": {"y_column": "deaths"}},
                ]
            },
        },
        "axis": {
            "type": "axis_controls",
            "args": {
                "use": "z",
                "options": ["cases", "deaths"],
                "default": "cases",
                "scale": False,
            },
        },
        "date": {"type": "date_picker"},
        "top10": {"type": "ranking", "width": 3, "args": {}},
        "globemap": {
            "type": "graph",
            "args": {"category": "map", "variant": "choropleth", "geo": "world"},
        },
    },
    "layout": [["agg", "axis", "date"], ["top10", "globemap"],],
    "connections": {
        "axis": {"globemap", "top10"},
        "date": {"globemap", "top10", "agg"},
    },
}

world_trends_page = {
    "dataid": "covid_world",
    "banks": {
        "axis": {"type": "axis_controls", "args": {"vertical": False}},
        "pick_country": {
            "type": "filter_set",
            "args": {"columns": ["country"], "vertical": False},
        },
        "window": {"type": "window_controls"},
        "analytics": {"type": "analytics_set", "args": {"vertical": True}},
        "trend": {"type": "graph"},
        "style": {"type": "style_controls"},
    },
    "layout": [["axis", "pick_country", "analytics", "window"], ["trend"], ["style"]],
    "connections": {
        "axis": {"trend"},
        "pick_country": {"trend"},
        "window": {"trend"},
        "analytics": {"trend"},
        "style": {"trend"},
    },
}

usgeo_page = {
    "dataid": "covid_us",
    "banks": {
        "agg": {
            "type": "indicators",
            "width": 3,
            "args": {
                "components": [
                    {"args": {"y_column": "cases"}},
                    {"args": {"y_column": "deaths"}},
                ]
            },
        },
        "axis": {
            "type": "axis_controls",
            "args": {
                "use": "z",
                "options": ["cases", "deaths"],
                "default": "cases",
                "scale": False,
            },
        },
        "date": {"type": "date_picker"},
        "top10": {"type": "ranking", "width": 3, "args": {}},
        "map_settings": {
            "type": "option_set",
            "args": {
                "components": [
                    {
                        "name": "geo",
                        "label": "Select geography",
                        "options": ["state", "county"],
                    },
                ]
            },
        },
        "countymap": {
            "type": "graph",
            "args": {"category": "map", "variant": "choropleth"},
        },
    },
    "layout": [["agg", "map_settings", "axis", "date"], ["top10", "countymap"],],
    "connections": {
        "axis": {"countymap", "top10"},
        "map_settings": {"countymap", "top10"},
        "date": {"countymap", "top10", "agg"},
    },
}

us_trends_page = {
    "dataid": "covid_us",
    "banks": {
        "axis": {"type": "axis_controls", "args": {"vertical": False}},
        "pick_state": {
            "type": "filter_set",
            "args": {"columns": ["state", "county"], "vertical": False},
        },
        "window": {"type": "window_controls"},
        "analytics": {"type": "analytics_set"},
        "trend": {"type": "graph"},
        "style": {"type": "style_controls"},
    },
    "layout": [["axis", "pick_state"], ["window", "analytics"], ["trend"], ["style"]],
    "connections": {
        "axis": {"trend"},
        "pick_state": {"trend"},
        "window": {"trend"},
        "analytics": {"trend"},
        "style": {"trend"},
    },
}

data_page = {
    "banks": {
        "covid_world_table": {
            "type": "data_table",
            "width": 12,
            "args": {
                "dataid": "covid_world",
                "default": ["date", "country", "cases", "deaths"],
            },
        },
        "covid_table": {
            "type": "data_table",
            "width": 12,
            "args": {
                "dataid": "covid_us",
                "default": ["date", "state", "cases", "deaths"],
            },
        },
    },
    "layout": [["covid_table"]],
    "connections": {},
}


descriptor = {
    "name": "demo",
    "theme": "flat sparse",
    "theme_dict": {},
    "appbar": {"title": "COVID in World/US", "subtitle": "Tracking case trends"},
    "data": {
        "covid_us": {"module": "loaddata.covid_us"},
        "covid_world": {"module": "loaddata.covid_world"},
    },
    "pages": {
        "globe": globe_page,
        "world_trends": world_trends_page,
        "us": usgeo_page,
        "us_trends": us_trends_page,
        "data": data_page,
    },
}


if __name__ == "__main__":
    from bento import bento

    app_def = bento.Bento(descriptor)
    app_def.write("cache/shared/active/generated.py")

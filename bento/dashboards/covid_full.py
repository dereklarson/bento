geo_page = {
    "dataid": "covid",
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

trends_page = {
    "dataid": "covid",
    "banks": {
        "axis": {"type": "axis_controls", "args": {"vertical": False}},
        "pick_state": {
            "type": "filter_set",
            "args": {"columns": ["state", "county"], "vertical": False},
        },
        "window": {"type": "window_controls"},
        "analytics": {"type": "analytics_set"},
        "trend": {
            "type": "graph",
            "args": {
                # "height": "350px",
                # "x_column": "date",
                # "y_column": "cases",
                # "x_scale": "date",
            },
        },
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
        "covid_table": {
            "type": "data_table",
            "width": 12,
            "args": {
                "dataid": "covid",
                "default": ["date", "state", "cases", "deaths"],
            },
        },
    },
    "layout": [["covid_table"]],
    "connections": {},
}


descriptor = {
    "name": "demo",
    "theme": "dark flat sparse",
    "appbar": {"title": "COVID in US", "subtitle": "Tracking case load by county"},
    "data": {"covid": {"module": "loaddata.covid_us"}},
    "pages": {"geo": geo_page, "trends": trends_page, "data": data_page},
}


if __name__ == "__main__":
    # Must do this first before importing bento, to inject environment vars
    from bento import bento

    app_def = bento.Bento(descriptor)
    app_def.write("gen.py")
    app_def.write_theme()

mars_page = {
    "title": "Mars Population",
    "subtitle": "Demonstrating graph options and style",
    "dataid": "mars",
    "banks": {
        "selector": {"type": "axis_controls", "args": {"use": "xy", "scale": True}},
        "filters": {"type": "filter_set", "args": {}},
        "agg": {
            "type": "indicators",
            "width": 2,
            "args": {
                "components": [
                    {
                        "args": {
                            "y_column": "population",
                            "fixed_filters": {"or": {"date": ["2149-04-21"]}},
                        }
                    }
                ]
            },
        },
        "traces": {"type": "graph"},
        "style": {
            "type": "style_controls",
            "args": {"vertical": True, "variants": ["scatter", "bar"]},
        },
    },
    "layout": [["selector", "filters", "agg"], ["traces"], ["style"]],
    "connections": {
        "style": {"traces"},
        "selector": {"traces"},
        "filters": {"traces", "agg"},
    },
}

stock_page = {
    "title": "Stock Prices",
    "subtitle": "Demonstrating analytical features",
    "dataid": "stock",
    "banks": {
        "selector": {
            "type": "axis_controls",
            "args": {"use": "y", "y.default": "open", "scale": True},
        },
        "filters": {
            "type": "filter_set",
            "width": 4,
            "args": {"vertical": True, "columns": ["symbol"]},
        },
        "analytics": {"type": "analytics_set"},
        "traces": {
            "type": "graph",
            "args": {"x_column": "date", "x_scale": "date", "mode": "lines"},
        },
    },
    "layout": [["selector", "filters", "analytics"], ["traces"]],
    "connections": {
        "selector": {"traces"},
        "analytics": {"traces"},
        "filters": {"traces"},
    },
}

covid_page = {
    "title": "COVID-19",
    "subtitle": "Tracking case load",
    "dataid": "covid",
    "banks": {
        "agg": {
            "type": "indicators",
            "width": 2,
            "args": {"components": [{"args": {"y_column": "cases"}}]},
        },
        "date": {"type": "date_picker"},
        "top10": {"type": "ranking", "args": {"key": "state", "column": "cases"}},
        "mapsettings": {
            "type": "option_set",
            "args": {
                "components": [
                    {
                        "name": "geo",
                        "label": "Select geography",
                        "options": ["us_states", "us_counties"],
                    },
                ]
            },
        },
        "countymap": {
            "type": "graph",
            "width": 7,
            "args": {"category": "map", "variant": "choropleth", "z_column": "cases",},
        },
    },
    "layout": [["agg", "date", "mapsettings"], ["top10", "countymap"], ["trend"],],
    "connections": {
        "mapsettings": {"countymap", "trend"},
        "date": {"countymap", "top10", "agg"},
    },
}

oilngas_page = {
    "dataid": "oil",
    "banks": {
        "selector": {"width": 3, "type": "axis_controls", "args": {"use": "xy"},},
        "daterange": {"width": 4, "type": "date_slider", "args": {"variant": "range"},},
        "filters": {
            "type": "filter_set",
            "args": {"columns": ["type", "status"], "vertical": True},
            "width": 4,
        },
        "aggregates": {
            "type": "indicators",
            "args": {
                "components": [
                    {"args": {"y_column": "wells"},},
                    {"args": {"y_column": "gas_produced"}, "unit": "cf"},
                    {"args": {"y_column": "oil_produced"}, "unit": "bbl"},
                    {"args": {"y_column": "water_produced"}, "unit": "bbl"},
                ],
            },
        },
        "barplot": {"type": "graph", "args": {"variant": "bar"}},
        "pieplot": {"type": "graph", "args": {"variant": "pie", "x_column": "type"}},
        "satellite": {
            "type": "graph",
            "width": 8,
            "args": {"category": "map", "variant": "scatter", "mapbox_center": "auto"},
        },
        "style": {"type": "style_controls"},
    },
    "layout": [
        ["daterange", "aggregates", "selector"],
        ["filters", "barplot"],
        ["pieplot", "satellite"],
    ],
    "connections": {
        "daterange": {"barplot", "aggregates", "pieplot",},
        "filters": {"barplot", "aggregates", "satellite",},
        "selector": {"barplot", "pieplot"},
    },
}

data_page = {
    "banks": {
        "mars_table": {"type": "data_table", "args": {"dataid": "mars"}},
        "oil_table": {"type": "data_table", "width": 6, "args": {"dataid": "oil"}},
        "stock_table": {"type": "data_table", "args": {"dataid": "stock"}},
        "covid_table": {"type": "data_table", "width": 6, "args": {"dataid": "covid"}},
    },
    "layout": [["mars_table", "oil_table"], ["stock_table", "covid_table"]],
    "connections": {},
}


descriptor = {
    "name": "demonstration",
    "theme": "dark",
    "appbar": {"title": "Bento Demo", "subtitle": "A gallery of Dash recreations"},
    "data": {
        "covid": {"module": "bento.sample_data.covid"},
        "mars": {"module": "bento.sample_data.mars"},
        "oil": {"module": "bento.sample_data.oil"},
        "stock": {"module": "bento.sample_data.stock"},
    },
    "pages": {
        "covid": covid_page,
        "oilngas": oilngas_page,
        "mars": mars_page,
        "stock": stock_page,
        "data": data_page,
    },
}


def serve():
    """Both writes and serves the demo dashboard
    It is used in the "bento-dash" console script supplied by setup.py
    """
    print("Running simple Bento demonstration...")
    import sys
    from bento import bento

    bento.Bento(descriptor).write()
    sys.path.append(".")

    from bento_app import app  # noqa

    app.run_server(host="0.0.0.0", port=8050, debug=False)


if __name__ == "__main__":
    from bento import bento

    bento.Bento(descriptor).write()

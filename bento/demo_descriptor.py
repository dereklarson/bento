mars_page = {
    "title": "Mars Population",
    "subtitle": "Demonstrating graph options and style",
    "dataid": "mars",
    "banks": {
        "selector": {"type": "axis_controls", "args": {"use": "xy"}},
        "filters": {"type": "filter_set", "args": {}},
        "agg": {
            "type": "indicators",
            "width": 2,
            "args": {
                "components": [
                    {
                        "args": {
                            "y_column": "population",
                            "fixed_filters": [("or", "date", ["2149-04-21"])],
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
        "selector": {"type": "axis_controls", "args": {"use": "y", "default": "open"},},
        "filters": {"type": "filter_set", "args": {"vertical": True}},
        "window": {"type": "window_controls"},
        "traces": {
            "type": "graph",
            "args": {"x_column": "date", "x_scale": "date", "mode": "lines"},
        },
    },
    "layout": [["selector", "filters", "window"], ["traces"]],
    "connections": {
        "selector": {"traces"},
        "window": {"traces"},
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
        "top10": {"type": "ranking", "args": {}},
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
        # "trend": {
        #     "type": "graph",
        #     "width": 6,
        #     "args": {"height": "350px", "x_column": "date", "y_column": "cases"},
        # },
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
        "selector": {
            "width": 3,
            "type": "axis_controls",
            "args": {"use": "xy", "scale": False},
        },
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

svm_page = {
    "dataid": "mars",
    "banks": {
        "selector": {"type": "axis_controls", "args": {"use": "xy", "vertical": True},},
        "data_settings": {
            "type": "option_set",
            "args": {
                "components": [
                    {
                        "name": "n_samples",
                        "options": [100, 200, 300, 400, 500],
                        "label": "Sample Size:",
                    },
                    {
                        "name": "noise",
                        "options": [0, 0.2, 0.4, 0.6, 0.8, 1.0],
                        "label": "Noise Level:",
                    },
                ]
            },
        },
        "heatmap": {"type": "graph"},
    },
    # "layout": [["selector", "data_settings"], ["heatmap"]],
    "layout": [["heatmap"]],
    "sidebar": ["selector", "data_settings"],
    "connections": {"data_settings": {"heatmap"}, "selector": {"heatmap"},},
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
    "name": "demo",
    # "theme": "dark flat sparse",
    "theme": "dark",
    "main": {"title": "Bento Demo", "subtitle": "A gallery of Dash recreations"},
    "data": {
        "covid": {"module": "bento.examples.covid"},
        "mars": {"module": "bento.examples.mars"},
        "oil": {"module": "bento.examples.oil"},
        "stock": {"module": "bento.examples.stock"},
        # "svm": {"module": "bento.examples.svm"},
    },
    "pages": {
        "covid": covid_page,
        "oilngas": oilngas_page,
        "mars": mars_page,
        "stock": stock_page,
        "data": data_page,
        # "svm": svm_page,
    },
}


if __name__ == "__main__":
    from bento import bento

    app_def = bento.Bento(descriptor)
    app_def.write("cache/shared/active/generated.py")

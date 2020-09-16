mars_page = {
    "title": "Mars Population",
    "subtitle": "Demonstrating graph options and style",
    "dataid": "mars",
    "banks": {
        "axes": {"type": "axis_controls", "axes": "xy", "scale": True},
        "filters": {"type": "selector"},
        "agg": {
            "type": "indicators",
            "width": 2,
            "components": [
                {
                    "args": {
                        "y_column": "population",
                        "fixed_filters": {"or": {"date": ["2149-08-07"]}},
                    }
                }
            ],
        },
        "traces": {"type": "graph"},
        # "style": {
        #     "type": "style_controls",
        #     "vertical": True, "variants": ["scatter", "bar"],
        # },
    },
    "layout": [["axes", "filters", "agg"], ["traces"], ["style"]],
    "connections": {
        "style": {"traces"},
        "axes": {"traces"},
        "filters": {"traces", "agg"},
    },
}

stock_page = {
    "title": "Stock Prices",
    "subtitle": "Demonstrating analytical features",
    "dataid": "stock",
    "banks": {
        "axes": {
            "type": "axis_controls",
            "axes": "y",
            "y.default": "open",
            "scale": True,
        },
        "filters": {
            "type": "selector",
            "width": 4,
            "vertical": True,
            "columns": ["symbol"],
        },
        "analytics": {"type": "analytics_set"},
        "traces": {
            "type": "graph",
            "x_column": "date",
            "x_scale": "date",
            "mode": "lines",
        },
    },
    "layout": [["axes", "filters", "analytics"], ["traces"]],
    "connections": {
        "axes": {"traces"},
        "analytics": {"traces"},
        "filters": {"traces"},
    },
}

oilngas_page = {
    "dataid": "oil",
    "banks": {
        "axes": {"width": 3, "type": "axis_controls", "axes": "xy"},
        "daterange": {"width": 4, "type": "date_control", "variant": "range"},
        "filters": {
            "type": "selector",
            "columns": ["type", "status"],
            "vertical": True,
            "width": 4,
        },
        "aggregates": {
            "type": "indicators",
            "components": [
                {"args": {"y_column": "wells"},},
                {"args": {"y_column": "gas_produced"}, "unit": "cf"},
                {"args": {"y_column": "oil_produced"}, "unit": "bbl"},
                {"args": {"y_column": "water_produced"}, "unit": "bbl"},
            ],
        },
        "barplot": {"type": "graph", "variant": "bar"},
        "pieplot": {"type": "graph", "variant": "pie", "x_column": "type"},
        "satellite": {
            "type": "graph",
            "width": 8,
            "category": "map",
            "variant": "scatter",
            "mapbox_center": "auto",
        },
    },
    "layout": [
        ["daterange", "aggregates", "axes"],
        ["filters", "barplot"],
        ["pieplot", "satellite"],
    ],
    "connections": {
        "daterange": {"barplot", "aggregates", "pieplot",},
        "filters": {"barplot", "aggregates", "satellite",},
        "axes": {"barplot", "pieplot"},
    },
}

data_page = {
    "banks": {
        "mars_table": {"type": "data_table", "dataid": "mars"},
        "oil_table": {"type": "data_table", "width": 6, "dataid": "oil"},
        "stock_table": {"type": "data_table", "width": 12, "dataid": "stock"},
    },
    "layout": [["mars_table", "oil_table"], ["stock_table"]],
    "connections": {},
}


descriptor = {
    "name": "demonstration",
    "theme": "dark",
    "appbar": {"title": "Bento Demo", "subtitle": "A gallery of Dash recreations"},
    "data": {
        "mars": {"module": "bento.sample_data.mars"},
        "oil": {"module": "bento.sample_data.oil"},
        "stock": {"module": "bento.sample_data.stock"},
    },
    "pages": {
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
    from bento.bento import Bento

    Bento(descriptor).write()
    sys.path.append(".")

    from bento_app import app  # noqa

    app.run_server(host="0.0.0.0", port=8050, debug=False)


if __name__ == "__main__":
    import inspect

    print("Writing demo to ./descriptor.py")
    lines = inspect.getsourcelines(inspect.getmodule(inspect.currentframe()))[0]

    with open("descriptor.py", "w") as fh:
        for line in lines:
            if "def serve():" in line:
                break
            fh.write(line)

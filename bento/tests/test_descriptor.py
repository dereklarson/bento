from loaddata import example
from bento import bento


def generate(output, repobase):
    series_page = {
        "banks": {
            "selector": {"args": {"use": "xy"}, "type": "axis_controls"},
            "windowing": {"type": "window_controls"},
            "style": {"type": "style_controls"},
            "filter_set": {"type": "filters"},
            "graph": {"type": "graph"},
        },
        "layout": [["selector", "style", "windowing", "filter_set"], ["graph"]],
        "connections": {
            "selector": {"graph": ["figure"]},
            "windowing": {"graph": ["figure"]},
            "style": {"graph": ["figure"]},
            "filter_set": {"graph": ["figure"]},
        },
    }

    map_page = {
        "banks": {
            "selector": {
                "args": {"use": "xy", "vertical": True},
                "type": "axis_controls",
            },
            "options": {
                "type": "option_set",
                "args": {
                    "components": [
                        {"name": "window", "options": [1, 7, 10], "label": "window"},
                        {
                            "name": "variant",
                            "options": ["normal", "bar"],
                            "label": "variant",
                        },
                        {
                            "name": "marker_border_width",
                            "options": [0.1, 0.3, 0.5, 0.8, 1.0],
                            "label": "marker border",
                        },
                    ]
                },
            },
            "style": {"type": "style_controls"},
            "graph": {"type": "graph"},
        },
        "layout": [["graph"]],
        "sidebar": ["selector", "style", "options"],
        "connections": {
            "style": {"graph": ["figure"]},
            "selector": {"graph": ["figure"]},
            "options": {"graph": ["figure"]},
        },
    }

    simple_desc = {
        "banks": {
            "selector": {"args": {"use": "xy"}, "type": "axis_controls"},
            "style": {"type": "style_controls"},
            "graph": {"type": "graph"},
        },
        "connections": {
            "style": {"graph": ["figure"]},
            "selector": {"graph": ["figure"]},
        },
    }

    descriptor = {
        "name": "mars",
        "theme": "dark",
        "data": {"location": repobase, "calls": {"dataname": example.load},},
        "mode": "condensed",
        "main": {"title": "Mars Dashboard", "subtitle": "Fabricated population data"},
        "pages": {"series": series_page, "map": map_page},
        # **simple_desc,
    }

    app_def = bento.Bento(descriptor)
    app_def.write(output)


if __name__ == "__main__":
    generate("cache/shared/active/generated.py", "./")

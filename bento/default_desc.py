from bento import bento
from loaddata import example


def generate(output, repobase):
    main_page = {
        "banks": {
            "selector": {"type": "axis_controls", "args": {"use": "xy"}},
            "filters": {"type": "filters"},
            "confmap": {"type": "graph"},
        },
        "layout": [["selector", "filters"], ["confmap"]],
        "connections": {
            "selector": {"confmap": ["figure"]},
            "filters": {"confmap": ["figure"]},
        },
    }

    descriptor = {
        "name": "example",
        "main": {"title": "Example Dashboard built with Aleph"},
        "pages": {"main": main_page},
        "data": {"location": repobase, "calls": {"dataname": example.load}},
    }

    app_def = bento.Bento(descriptor)
    app_def.write(output)

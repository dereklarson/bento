trends_page = {
    "dataid": "covid",
    "banks": {
        "axis": {"type": "axis_controls", "args": {"use": "xy", "scale": True}},
        "trend": {"type": "graph"},
    },
    "layout": [["axis"], ["trend"]],
    "connections": {"axis": {"trend"}},
}

descriptor = {
    "appbar": {
        "title": "Sample US covid data",
        "subtitle": "A simple, example Bento dashboard",
    },
    "data": {"covid": {"module": "bento.sample_data.covid"}},
    "pages": {"trends": trends_page},
}


if __name__ == "__main__":
    from bento import bento

    bento.Bento(descriptor).write()

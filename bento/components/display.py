from bento import Component


class graph(Component):
    def __init__(self, children="<Indicator>", **kwargs):
        comp_args = {
            "style": {"visibility": "hidden"},
        }
        if "height" in kwargs:
            comp_args["style"]["height"] = kwargs["height"]
        super().__init__("dcc", "Graph", comp_args, **kwargs)

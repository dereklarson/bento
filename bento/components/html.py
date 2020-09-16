from bento import Component


class indicator(Component):
    def __init__(self, children="<Indicator>", **kwargs):
        comp_args = {"children": children}
        super().__init__("html", "H3", comp_args, **kwargs)


class div(Component):
    def __init__(self, children="<Div>", **kwargs):
        comp_args = {"children": children}
        super().__init__("html", "Div", comp_args, **kwargs)

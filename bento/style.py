# These are CSS styles that roughly implement Material Design components
from bento.common import dictutil
from bento import named_themes

import colorsys


def elevation(elev):
    if not elev:
        return {}
    return {"boxShadow": f"1px 1px {elev}px 1px #888888"}


def grid_columns(n_col, pad_pct):
    col_size = (100 + pad_pct) / n_col - pad_pct
    return f"repeat({n_col}, {col_size:.2f}%)"


def flip_color(hex_color, offset_factor=1):
    """ Mirrors the hex color along the brightness axis, e.g #eeeeee -> #111111 """
    if len(hex_color) != 7:
        raise Exception(f"Color {hex_color} is not in #rrggbb format.")
    rgb = [int(hex_color[x : x + 2], 16) for x in [1, 3, 5]]
    hls = list(colorsys.rgb_to_hls(*rgb))
    # Reverse the lightness level
    hls[1] = 255 - hls[1]
    new_rgb = colorsys.hls_to_rgb(*hls)
    rgb2 = [min(255, max(0, int(level))) for level in new_rgb]
    return f"#{rgb2[0]:02x}{rgb2[1]:02x}{rgb2[2]:02x}"


def darken_color(hex_color, offset_factor=0.7):
    """ Mirrors the hex color along the brightness axis, e.g #eeeeee -> #111111 """
    if len(hex_color) != 7:
        raise Exception(f"Color {hex_color} is not in #rrggbb format.")
    rgb = [int(hex_color[x : x + 2], 16) for x in [1, 3, 5]]
    hls = list(colorsys.rgb_to_hls(*rgb))
    # Reduce lightness as defined by offset_factor
    hls[1] *= offset_factor
    new_rgb = colorsys.hls_to_rgb(*hls)
    rgb2 = [min(255, max(0, int(level))) for level in new_rgb]
    return f"#{rgb2[0]:02x}{rgb2[1]:02x}{rgb2[2]:02x}"


theme_keywords = {
    "tight": {"pad_unit": 2, "pad_pct": 0.5, "font__size": "1.3rem"},
    "sparse": {"pad_unit": 8, "pad_pct": 1.5, "font__size": "1.7rem"},
    "loose": {"pad_unit": 16, "pad_pct": 2.5, "font__size": "1.9rem"},
    "flat": {"elevation": 0,},
}


class BentoStyle:
    def __init__(self, theme="", theme_dict=None, layout=(12, 12)):
        # Default to the Bento theme
        self.spec = named_themes.bento
        self.spec["class_name"] = "bento-theme"  # Required for dropdowns, etc.

        # Passing a string assumes using theme keywords e.g. "dark flat"
        for word in theme.split(" "):
            self.spec.update(theme_keywords.get(word, {}))
            if word == "dark":
                for key in self.spec:
                    if "color" in key:
                        if "primary" in key or "secondary" in key:
                            self.spec[key] = darken_color(self.spec[key])
                        else:
                            self.spec[key] = flip_color(self.spec[key])
                self.spec["map__mapbox_style"] = "carto-darkmatter"
        if theme_dict:
            self.spec.update(dictutil.flatten(theme_dict))

        self.layout = {"row": layout[0], "columns": layout[1]}

        # Main defines the whole-page theme which will get inherited by children
        self.main = {
            "height": "100vmax",
            "textAlign": "center",
            "fontFamily": self.spec["font__family"],
            "fontSize": self.spec["font__size"],
            "color": self.spec["color__on_surface"],
            "backgroundColor": self.spec["color__background"],
        }

        self.page = {}
        self.appbar = {
            **elevation(self.spec["elevation"]),
            "backgroundColor": self.spec["color__primary"],
            "color": self.spec["color__on_primary"],
            "display": "flex",
            "flexDirection": "row",
            "justifyContent": "space-between",
            "background-size": "100%",
        }

        # Most components besdies the App Bar are contained in the page
        self.titles = {
            "display": "flex",
            "flexDirection": "row",
            "margin": 0,
            "paddingLeft": 24,
            "alignSelf": "flex-start",
            "alignItems": "flex-end",
        }
        self.h1 = {"margin": 0}
        self.h3 = {"margin": 0, "paddingLeft": 24, "fontStyle": "italic"}
        self.link_set = {"display": "flex", "flexDirection": "row"}
        self.link = {"display": "flex"}
        self.button = {"align-self": "center"}

        self.grid = {
            "display": "grid",
            "paddingTop": f"{self.spec['pad_pct']}%",
            "gridGap": f"{self.spec['pad_pct']}%",
            "rowGap": f"{self.spec['pad_pct'] * 1.4}%",
            "gridTemplateColumns": grid_columns(
                self.layout["columns"], self.spec["pad_pct"]
            ),
            "gridTemplateRows": "auto",
        }

        # Special components
        self.graph = {
            # TODO Figure out how to add this in as additional margin?
            # "margin": {
            #     "l": 16 + 4 * self.spec["pad_unit"],
            #     "b": 40 + 4 * self.spec["pad_unit"],
            #     "t": 40 + 4 * self.spec["pad_unit"],
            #     "r": 40 + 4 * self.spec["pad_unit"],
            # },
            # "transition": {"duration": 500},
            "font": {"color": self.spec["color__on_surface"]},
            "yaxis": {"gridcolor": self.spec["color__primary"]},
            "xaxis": {"gridcolor": self.spec["color__primary"]},
            "autosize": True,
            "hovermode": "closest",
            "paper_bgcolor": self.spec["color__surface"],
            "plot_bgcolor": self.spec["color__plot_bg"],
            # For maps
            "mapbox_style": self.spec["map__mapbox_style"],
            "geo_oceancolor": "LightBlue",
            "geo_lakecolor": "Blue",
            "geo_landcolor": self.spec["color__plot_bg"],
            "geo_bgcolor": self.spec["color__surface"],
        }

        self.trace = {}

        self.summary = {"backgroundColor": self.spec["color__primary"]}

        # Smaller scale objects: Paper > Bar > Block
        self.paper = {
            **elevation(self.spec["elevation"]),
            "backgroundColor": self.spec["color__surface"],
            # "textAlign": "center",
            "display": "flex",
            "flexDirection": "column",
            "padding": self.spec["pad_unit"],
        }

        self.bar = {
            "display": "flex",
            "flex-direction": "row",
            "justify-content": "space-evenly",
        }

        self.label = {}

        self.block = {
            "display": "flex",
            "flexDirection": "column",
            "flexGrow": "1",
            "padding": self.spec["pad_unit"],
        }

        # NOTE We need an entry here for every component library, as is
        self.html = {}
        self.dcc = {}
        # NOTE This fixes x-scrolling for data_table
        self.dash_table = {"overflowX": "hidden"}

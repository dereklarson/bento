# These are CSS styles that roughly implement Material Design components


def elevation(elev):
    if not elev:
        return {}
    return {"boxShadow": f"1px 1px {elev}px 1px #888888"}


def grid_columns(n_col, pad_pct):
    col_size = (100 + pad_pct) / n_col - pad_pct
    return f"repeat({n_col}, {col_size:.2f}%)"


dark_text = "#212529"  # Default text color for a light background
light_text = "#aaaaaa"  # Default text color for a dark background
theme_text = "#7FDBFF"  # A light blue
theme_text = "#f7021f"  # A Marsish red?

# TODO Abstract primary colors away with the "50-1000" system
themes = {
    "light": {
        # Colors
        "class_name": None,
        "color": dark_text,
        "backup_color": dark_text,
        "primary": "#ed4415",
        "app_bar": "#ed4415",
        "main_color": "#FCFCFC",
        "paper_color": "#F1F1F1",
        "plot_bg_color": "#E8E9EA",
        # Density
        "pad_unit": 4,
        "pad_pct": 1.0,
        # Flatness
        "elevation": 4,
    },
    "dark": {
        "class_name": "bento-theme",  # Required for dropdowns, etc.
        "color": theme_text,
        "backup_color": light_text,
        "primary": "#8d3212",
        "app_bar": "#222222",
        "main_color": "#121212",
        "paper_color": "#222222",
        "plot_bg_color": "#333333",
    },
    "tight": {"pad_unit": 2, "pad_pct": 0.5},
    "sparse": {"pad_unit": 8, "pad_pct": 1.5},
    "loose": {"pad_unit": 16, "pad_pct": 3.0},
    "flat": {"elevation": 0,},
}


class BentoStyle:
    def __init__(self, theme=None, layout=(12, 12)):
        self.theme = themes["light"]
        for word in theme.split(" "):
            self.theme.update(themes.get(word, {}))

        self.layout = {"row": layout[0], "columns": layout[1]}

        # Main defines the whole-page theme which will get inherited by children
        self.main = {
            "height": "100vmax",
            "textAlign": "center",
            # "fontFamily": "Verdana",
            "color": self.theme["color"],
            "backgroundColor": self.theme["main_color"],
        }

        self.page = {}
        self.app_bar = {
            **elevation(self.theme["elevation"]),
            "backgroundColor": self.theme["app_bar"],
            "display": "flex",
            "flexDirection": "row",
            "justifyContent": "space-between",
        }

        # Most components besdies the App Bar are contained in the page
        self.titles = {
            "display": "flex",
            "flexDirection": "row",
            "margin": 0,
            "paddingLeft": 6 * self.theme["pad_unit"],
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
            "paddingTop": f"{self.theme['pad_pct']}%",
            "gridGap": f"{self.theme['pad_pct']}%",
            "rowGap": f"{self.theme['pad_pct'] * 1.4}%",
            "gridTemplateColumns": grid_columns(
                self.layout["columns"], self.theme["pad_pct"]
            ),
            "gridTemplateRows": "auto",
        }

        # Special components
        self.graph = {
            # TODO Figure out how to add this in as additional margin?
            # "margin": {
            #     "l": 16 + 4 * self.theme["pad_unit"],
            #     "b": 40 + 4 * self.theme["pad_unit"],
            #     "t": 40 + 4 * self.theme["pad_unit"],
            #     "r": 40 + 4 * self.theme["pad_unit"],
            # },
            # "transition": {"duration": 500},
            "font": {"color": self.theme["backup_color"]},
            "yaxis": {"gridcolor": self.theme["primary"]},
            "xaxis": {"gridcolor": self.theme["primary"]},
            "autosize": True,
            "hovermode": "closest",
            "geo_oceancolor": "LightBlue",
            "geo_lakecolor": "Blue",
            "geo_landcolor": self.theme["plot_bg_color"],
            "geo_bgcolor": self.theme["paper_color"],
            "paper_bgcolor": self.theme["paper_color"],
            "plot_bgcolor": self.theme["plot_bg_color"],
        }

        self.trace = {}

        # Smaller scale objects: Paper > Bar > Block
        self.paper = {
            **elevation(self.theme["elevation"]),
            "backgroundColor": self.theme["paper_color"],
            "textAlign": "center",
            "display": "flex",
            "flexDirection": "column",
            "padding": self.theme["pad_unit"],
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
            "padding": self.theme["pad_unit"],
        }

        # NOTE We need an entry here for every component library, as is
        self.html = {}
        self.dcc = {}
        # NOTE This fixes x-scrolling for data_table
        self.dash_table = {"overflowX": "hidden"}

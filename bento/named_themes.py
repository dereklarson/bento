gray = {}
gray[100] = "#f8f9fa"
gray[200] = "#ecf0f1"
gray[300] = "#dee2e6"
gray[400] = "#ced4da"
gray[500] = "#b4bcc2"
gray[600] = "#95a5a6"
gray[700] = "#7b8a8b"
gray[800] = "#343a40"
gray[900] = "#212529"

blue = "#133C93"
indigo = "#6610f2"
purple = "#6f42c1"
pink = "#e83e8c"
red = "#e74c3c"
orange = "#fd7e14"
yellow = "#f39c12"
green = "#18bc9c"
teal = "#20c997"
cyan = "#3498db"

# This the default 'Bento' theme
# NOTE Still plenty of work to do fleshing this out (variants, secondaries)
bento = {
    # Colors
    "color__primary": blue,
    "color__secondary": purple,
    "color__on_primary": gray[200],
    "color__on_surface": gray[800],
    "color__on_surface_secondary": gray[700],
    "color__background": gray[100],
    "color__info": cyan,
    "color__warning": yellow,
    "color__danger": red,
    "color__success": green,
    "color__surface": gray[300],
    "color__plot_bg": gray[500],
    # Density
    "pad_unit": 4,
    "pad_pct": 1.0,
    # Flatness
    "elevation": 4,
    # Font
    "font__family": ["Lato", "Roboto", "sans-serif"],
    "font__size": "1.5rem",
    # Map
    "map__mapbox_style": "carto-positron",
}

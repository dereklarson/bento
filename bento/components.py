"""These are a set of functions that wrap and facilitate use of dash components.
A list of goals for these functions:
    * Allow easy templating of a user's intended Dash app
    * Provide convenient default values
    * Don't do anything irreversible
"""
import math

from bento.common import logger, logutil, dictutil  # noqa
from bento import util as butil

logging = logger.fancy_logger(__name__)

# TODO Find a place for constants like this
MAX_OPTIONS = 100


def _create(component_class, id_dict, args, lib="dcc", suffix="", label=None, **kwargs):
    """Helps wrap Dash components so they can be easily written out via Jinja2"""
    bankid, name, pageid = dictutil.pluck(id_dict)
    cid = f"{pageid}/{bankid}|{name}{suffix}"
    comp = {
        "lib": lib,
        "component": component_class,
        "label": label,
        "args": {
            "id": cid,
            **args,
            # Allows users to supply arguments to Dash components via the descriptor
            **dictutil.extract_path(f"{component_class}.", kwargs),
        },
    }
    return cid, comp


# --- The rest are all component wrappers ---
# @logutil.loginfo(level='debug')
def graph(id_dict, **kwargs):
    # TODO Flesh this out
    # This sets the graphs to take up space but not be visible prior to callback
    args = {"style": {"visibility": "hidden"}}
    if "height" in kwargs:
        args["style"]["height"] = kwargs["height"]
    return _create("Graph", id_dict, args, **kwargs)


def radio(id_dict, options, label=None, **kwargs):
    args = {**butil.gen_options(options)}
    return _create("RadioItems", id_dict, args, label=label, **kwargs)


# @logutil.loginfo(level="debug")
def dropdown(id_dict, options, label=None, **kwargs):
    args = {**butil.gen_options(options)}
    if len(args["options"]) > MAX_OPTIONS:
        if "overflow" in options:
            logging.warning(f"Replacing {id_dict} option list with 'generator'")
            args.pop("options")
            args.pop("value")
            args["overflow"] = f"butil.gen_options({options['overflow']})"
        else:
            logging.warning(
                f"{id_dict} has many options {len(args['options'])} and"
                "might cause performance issues"
            )
    return _create("Dropdown", id_dict, args, label=label, **kwargs)


def slider(id_dict, series, label=None, marks=False, variant="auto", **kwargs):
    # TODO Use dict extraction
    args = {
        "value": kwargs.get("value") or series.min(),
        "min": series.min(),
        "max": series.max(),
    }
    if variant == "date":
        args = {
            "value": kwargs.get("value") or int(series.min()),
            "min": int(series.min()),
            "max": int(series.max()),
        }

    if marks:
        args["marks"] = butil.gen_marks(series, variant)
        args["step"] = None
    return _create("Slider", id_dict, args, label=label, **kwargs)


def range_slider(id_dict, series, label=None, marks=None, **kwargs):
    spacing = math.ceil(len(series) / 10)
    args = {
        "min": series.min(),
        "max": series.max(),
        "value": [series.min(), series.max()],
        "marks": {str(item): str(item) for item in sorted(series)[::spacing]},
    }
    return _create("RangeSlider", id_dict, args, label=label, **kwargs)


def date_picker(id_dict, series, label=None, variant="single", **kwargs):
    args = {
        "min_date_allowed": series.min(),
        "max_date_allowed": series.max(),
        "initial_visible_month": series.max(),
        "date": series.max(),
    }
    return _create("DatePickerSingle", id_dict, args, label=label, **kwargs)


def stepper(id_dict, **kwargs):
    args = {
        "disabled": True,
        "interval": 0,
        "n_intervals": 0,
    }
    return _create("Interval", id_dict, args, label=None, **kwargs)


def table(id_dict, label=None, **kwargs):
    args = {
        "page_action": "none",
        "filter_action": "native",
        "sort_action": "native",
        "style_table": {"overflowX": "auto", "overflowY": "auto", "height": "300px",},
        # NOTE This is needed until Plotly fixes name collision with Bootstrap Grid css
        "css": [{"selector": ".row-1", "rule": "margin-right: 0px; margin-left: 0px"},],
    }
    return _create("DataTable", id_dict, args, lib="dash_table", label=label, **kwargs)


def indicator(id_dict, label=None, **kwargs):
    args = {"children": "<Indicator>"}
    return _create("H3", id_dict, args, lib="html", label=label, **kwargs)


def div(id_dict, label=None, **kwargs):
    args = {"children": "<Div>"}
    return _create("Div", id_dict, args, lib="html", label=label, **kwargs)

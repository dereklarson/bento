from bento import Component
from bento import util as butil
from bento.common import logger, logutil, dictutil  # noqa

logging = logger.fancy_logger(__name__)

# Used to limit how many explicitly written out options will appear in the application
# code for a given component. When there are few options, it is sensible to list them,
# but when there are hundreds or more, it is ideal to hide these behind some utility
# code.
MAX_OPTIONS = 100


class date_picker(Component):
    def __init__(self, options, variant="single", **kwargs):
        args = {
            "min_date_allowed": options.min(),
            "max_date_allowed": options.max(),
            "initial_visible_month": options.max(),
        }
        if variant == "single":
            component = "DatePickerSingle"
            args["date"] = options.max()
        elif variant == "range":
            component = "DatePickerRange"
            args["start_date"] = options.min()
            args["end_date"] = options.max()
        super().__init__("dcc", component, args, **kwargs)


class dropdown(Component):
    def __init__(self, options, multi=False, **kwargs):
        args = {**butil.gen_options(options, multi=multi)}
        if len(args["options"]) > MAX_OPTIONS:
            if "overflow" in options:
                args.pop("options")
                args.pop("value")
                args["overflow"] = f"butil.gen_options({options['overflow']}, [])"
            else:
                logging.warning(
                    f"Dropdown has many options {len(args['options'])} and"
                    "might cause performance issues"
                )
        super().__init__("dcc", "Dropdown", args, **kwargs)


class selection_list(Component):
    def __init__(self, options, multi=False, **kwargs):
        args = {**butil.gen_options(options, multi=multi)}
        if multi:
            super().__init__("dcc", "Checklist", args, **kwargs)
        else:
            super().__init__("dcc", "RadioItems", args, **kwargs)


class slider(Component):
    def __init__(self, options, variant="single", marks=False, **kwargs):
        args = {
            "value": kwargs.get("value") or options.min(),
            "min": options.min(),
            "max": options.max(),
        }
        if marks:
            args["marks"] = butil.gen_marks(options, variant)
            args["step"] = None

        if variant == "single":
            component = "Slider"
        elif variant == "range":
            args["value"] = [options.min(), options.max()]
            component = "RangeSlider"
        super().__init__("dcc", component, args, **kwargs)

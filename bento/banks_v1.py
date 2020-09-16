# import dash
import numpy as np
import pandas as pd

from bento.common import logger, logutil, codeutil, dictutil  # noqa
import bento.components as bc

from bento import util as butil


logging = logger.fancy_logger(__name__)


class BentoBanks:
    def __init__(self, data):
        self.data = data
        # We record all registered IDs to help with connections later

        self.outputs = {}
        self.callbacks = {}

        self.connectors = {}

    # @logutil.loginfo(level='debug')
    def _align(self, blocks, vertical, block_size):
        if vertical:
            layout = np.vstack(blocks)
            ideal_height = int(len(blocks) * block_size["ideal"][0])
            min_height = int(len(blocks) * block_size["min"][0])
            sizing = {
                "ideal": [ideal_height, block_size["ideal"][1]],
                "min": [min_height, block_size["min"][1]],
            }
        else:
            layout = np.hstack(blocks)
            ideal_width = int(len(blocks) * block_size["ideal"][1])
            min_width = int(len(blocks) * block_size["min"][1])
            sizing = {
                "ideal": [block_size["ideal"][0], ideal_width],
                "min": [block_size["min"][0], min_width],
            }

        return layout, sizing

    def info(self, uid, dataid, vertical=False, text="<info>", **kwargs):
        id_dict = {"name": f"text", **uid}
        # TODO Find what good defaults are and allow overrides
        kwargs = {
            "Div.style": {
                "textAlign": "left",
                "lineHeight": 1.2,
                "fontStyle": "italic",
            },
            **kwargs,
        }
        div_id, div = bc.div(id_dict, children=text, label=None, **kwargs)

        blocks = [[[div]]]
        block_size = {"ideal": [2, 4], "min": [1, 1]}
        return self._align(blocks, vertical, block_size)

    def ranking(self, uid, dataid, nformat=None, **kwargs):
        id_dict = {"name": f"ranking", **uid}
        kwargs = {"Div.style": {"textAlign": "left"}, **kwargs}
        div_id, div = bc.div(id_dict, label=None, **kwargs)

        # TODO Universal formatting is a pain, but see what we can do to improve this
        nformat = ".7g"

        # TODO Weigh in on whether using "geo" is the best 'key' (9L down) default
        callback_name = f"{uid['pageid']}_{uid['bankid']}__update_ranking"
        callback_code = f"""
            data = _global_data["{dataid}"]
            idf = data["df"]
            inputs = dictutil.process_inputs(dash.callback_context.inputs)

            filters = butil.prepare_filters(inputs)
            fdf = butil.filter_df(idf, filters=filters)

            column = dictutil.extract_unique("_column", inputs)
            geo = dictutil.extract_unique("geo", inputs)
            inputs.update({{"key": [geo, "fips"], "text_key": geo, "column": column}})
            inputs.update({kwargs})

            children = [
                html.H4(f"Top in {{inputs['column'].title()}}", style=classes.h4)
                ]
            for item in butil.rank(fdf, **inputs):
                text = [
                  html.Span(f"{{item[1]:{nformat}}}", style=classes.rank_value),
                  html.Span(f"      {{item[0]}}")
                  ]
                children.extend([html.Hr(), html.Span(text)])
            return children
            """

        self.callbacks[div_id] = {
            "provides": ["children"],
            "name": callback_name,
            "code": codeutil.format_code(callback_code),
        }

        blocks = [[[div]]]
        block_size = {"ideal": [4, 2], "min": [1, 1]}
        return self._align(blocks, True, block_size)

    def option_set(self, uid, components, vertical=True, **kwargs):
        blocks = []
        for comp in components:
            id_dict = {"name": comp["name"], **uid}
            label = comp["label"]
            # Default to dropdown
            ctype = bc.dropdown
            kwargs = {"Dropdown.clearable": False, **kwargs}
            options = comp["options"]
            if isinstance(comp["options"], str) and len(comp["options"] <= 3):
                ctype = bc.radio
            elif isinstance(comp["options"][0], (int, float)):
                ctype = bc.slider
                options = pd.Series(comp["options"])
            cid, optcomp = ctype(id_dict, options, label=label, marks=True, **kwargs)
            blocks.append([[optcomp]])
            self.outputs[cid] = "value"

        block_size = {"ideal": [3, 2], "min": [1, 1]}
        return self._align(blocks, vertical, block_size)

    def style_controls(self, uid, dataid, variants=(), vertical=False, **kwargs):
        blocks = []

        # A dropdown to select the line mode
        id_dict = {"name": "mode", **uid}
        options = ["lines+markers", "lines", "markers"]
        kwargs = {"Dropdown.clearable": False}
        mode_id, line_mode = bc.dropdown(id_dict, options, "Mode", **kwargs)
        self.outputs[mode_id] = "value"

        top_row = []
        if variants:
            id_dict = {"name": "variant", **uid}
            kwargs = {"Dropdown.clearable": False, **kwargs}
            label = "Select Graph Variant"
            var_id, variant = bc.dropdown(id_dict, variants, label, **kwargs)
            self.outputs[var_id] = "value"
            top_row.append(variant)

            # The radio buttons will be fed by the selected axis
            self.connectors[mode_id] = {
                "inputs": [(var_id, "value")],
                "outputs": [(mode_id, "options"), (mode_id, "value")],
            }

            callback_name = f"{uid['pageid']}_{uid['bankid']}__update_mode"
            callback_code = f"""
                inputs = dictutil.process_inputs(dash.callback_context.inputs)
                variant = dictutil.extract_unique("variant", inputs)
                options = ["lines+markers", "lines", "markers"]
                if variant == "bar":
                    options = ["group", "stack", "relative"]
                option_dict = butil.gen_options(options)
                return option_dict["options"], option_dict["value"]
                """

            self.callbacks[mode_id] = {
                "provides": ["options", "value"],
                "name": callback_name,
                "code": codeutil.format_code(callback_code),
            }
        top_row.append(line_mode)

        # Two sliders for the size of the markers and line width
        sizes = pd.Series([5, 20])
        id_dict = {"name": "marker_size", **uid}
        cid, marker_size = bc.slider(id_dict, sizes, "Marker Size", value=10, **kwargs)
        self.outputs[cid] = "value"
        sizes = pd.Series([1, 10])
        id_dict = {"name": "line_width", **uid}
        cid, line_width = bc.slider(id_dict, sizes, "Line Width", **kwargs)
        self.outputs[cid] = "value"
        bottom_row = [marker_size, line_width]

        block_size = {"ideal": [2, 4], "min": [1, 2]}
        blocks = [[top_row, bottom_row]]
        return self._align(blocks, vertical, block_size)

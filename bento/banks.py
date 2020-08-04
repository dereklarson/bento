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

    # @logutil.loginfo(level='debug')
    def axis_controls(
        self, gid, dataid, use, multi=None, scale=False, vertical=False, **kwargs,
    ):
        blocks = []
        for axis_idx, axis in enumerate(use):
            # Define the dropdown to select a column to display on the axis
            label = f"{axis}-Axis Data".title()
            id_dict = {"name": f"{axis}_column", **gid}
            cargs = {"Dropdown.clearable": False, **kwargs}

            if multi and axis in multi:
                cargs["Dropdown.multi"] = True

            default_idx = min(axis_idx, len(self.data[dataid]["columns"]) - 1)
            option_args = dictutil.extract_path(f"{axis}.", kwargs)
            options = {
                "options": self.data[dataid]["columns"],
                "default": self.data[dataid]["columns"][default_idx],
                **option_args,
            }
            drop_id, dropdown = bc.dropdown(id_dict, options, label=label, **cargs)
            self.outputs[drop_id] = "value"

            if not scale:
                blocks.append([[dropdown]])
                continue

            # Define the radio buttons to select the axis scale
            id_dict = {"name": f"{axis}_scale", **gid}
            radio_id, radio = bc.radio(id_dict, ["linear", "log"])
            self.outputs[radio_id] = "value"

            # The radio buttons will be fed by the selected axis
            self.connectors[radio_id] = {
                "inputs": [(drop_id, "value")],
                "outputs": [(radio_id, "options"), (radio_id, "value")],
            }

            # TODO includes temporary multi-column support
            callback_name = f"{gid['pageid']}_{gid['bankid']}__update_{axis}_radio"
            callback_code = f"""
                inputs = dictutil.process_inputs(dash.callback_context.inputs)
                column = dictutil.extract_unique("_column", inputs)

                if isinstance(column, list):
                    column = column[0]

                col_type = data["{dataid}"]['types'].get(column, 'all')
                options = ["linear", "log", "date"]
                if col_type in (float, int):
                    options = ['linear', 'log']
                elif col_type in ('date', 'datetime'):
                    options = ['date']
                option_dict = butil.gen_options(options)
                return option_dict["options"], option_dict["value"]
                """

            self.callbacks[radio_id] = {
                "provides": ["options", "values"],
                "name": callback_name,
                "code": codeutil.format_code(callback_code),
            }

            blocks.append([[dropdown], [radio]])

        block_size = {"ideal": [1, 2], "min": [1, 1]}
        return self._align(blocks, vertical, block_size)

    # TODO In Progress
    def analytics_set(
        self,
        gid,
        dataid,
        window=True,
        normalize=True,
        calculus=True,
        vertical=False,
        **kwargs,
    ):
        blocks = []
        if window:
            id_dict = {"name": "window_transform", **gid}
            label = "Averaging Window"
            # TODO Insert calculation of length of time between datapoints
            windows = [(1, "Day"), (7, "Week"), (30, "Month"), (365, "Year")]
            options = {
                "options": [{"value": item[0], "label": item[1]} for item in windows],
                "value": 1,
            }
            kwargs = {"Dropdown.clearable": False}
            cid, window = bc.dropdown(id_dict, options, label, **kwargs)
            self.outputs[cid] = "value"
            blocks.append([[window]])

        if normalize:
            id_dict = {"name": f"norm_transform", **gid}
            label = f"Normalize by:".title()
            options = {
                "options": ["None", "Max"],
                "default": "None",
            }
            drop_id, dropdown = bc.dropdown(id_dict, options, label=label, **kwargs)
            self.outputs[drop_id] = "value"
            blocks.append([[dropdown]])

        if calculus:
            id_dict = {"name": f"calc_transform", **gid}
            label = f"Sums and Rates".title()
            options = {
                "options": ["Acceleration", "Rate", "None", "Cumulative"],
                "default": "None",
            }
            drop_id, dropdown = bc.dropdown(id_dict, options, label=label, **kwargs)
            self.outputs[drop_id] = "value"
            blocks.append([[dropdown]])

        block_size = {"ideal": [2, 2], "min": [1, 2]}
        return self._align(blocks, vertical, block_size)

    def date_slider(
        self, gid, dataid, column=None, variant="single", vertical=False, **kwargs
    ):
        df = self.data[dataid]["df"]
        default = "date" if "date" in df.columns else self.data[dataid]["columns"][0]
        column = column or default
        id_dict = {"name": f"{column}_filter", **gid}
        series = df[column].unique()
        if variant == "single":
            label = f"Select {column}:"
            slider_id, slider = bc.slider(
                id_dict, series, label, marks=True, variant="date"
            )
        elif variant == "range":
            label = f"Select range of {column}:"
            slider_id, slider = bc.range_slider(id_dict, series, label, marks=True)
        self.outputs[slider_id] = "value"

        blocks = [[[slider]]]
        block_size = {"ideal": [2, 4], "min": [1, 2]}
        return self._align(blocks, vertical, block_size)

    def date_combo(
        self, gid, dataid, column=None, variant="single", vertical=False, **kwargs
    ):
        df = self.data[dataid]["df"]
        default = "date" if "date" in df.columns else self.data[dataid]["columns"][0]
        column = column or default
        series = np.unique(df[column].dt.to_pydatetime())
        sl_series = np.unique(df[column])
        if variant == "single":
            id_dict = {"name": f"{column}_picker", **gid}
            label = f"Select {column}:"
            picker_id, picker = bc.date_picker(id_dict, series, label, variant=variant)
            id_dict = {"name": f"{column}_filter", **gid}
            slider_id, slider = bc.slider(id_dict, sl_series, None, marks=False)
        elif variant == "range":
            label = f"Select range of {column}:"
            picker_id, picker = bc.date_picker(id_dict, series, label)
        # self.outputs[picker_id] = "date"
        self.outputs[slider_id] = "value"

        blocks = [[[picker], [slider]]]
        block_size = {"ideal": [2, 2], "min": [1, 1]}
        return self._align(blocks, vertical, block_size)

    def date_picker(
        self, gid, dataid, column=None, variant="single", vertical=False, **kwargs
    ):
        df = self.data[dataid]["df"]
        default = "date" if "date" in df.columns else self.data[dataid]["columns"][0]
        column = column or default
        id_dict = {"name": f"{column}_filter", **gid}
        series = np.unique(df[column].dt.to_pydatetime())
        if variant == "single":
            label = f"Select {column}:"
            picker_id, picker = bc.date_picker(id_dict, series, label, variant=variant)
        elif variant == "range":
            label = f"Select range of {column}:"
            picker_id, picker = bc.date_picker(id_dict, series, label)
        self.outputs[picker_id] = "date"

        blocks = [[[picker]]]
        block_size = {"ideal": [2, 2], "min": [1, 1]}
        return self._align(blocks, vertical, block_size)

    def indicators(self, gid, dataid, components, vertical=False, **kwargs):
        blocks = []
        for ind_comp in components:
            name = ind_comp.get("name", ind_comp["args"]["y_column"])
            label = ind_comp.get("label", butil.titlize(name))
            id_dict = {"name": f"{name}_indicator", **gid}
            kwargs = {"Indicator.style": {"border": "1px solid gray"}, **kwargs}
            cid, comp = bc.indicator(id_dict, label=label, **kwargs)

            callback_name = f"{gid['pageid']}_{gid['bankid']}__update_{name}"
            callback_code = f"""
                idf = data["{dataid}"]["df"]
                inputs = dictutil.process_inputs(dash.callback_context.inputs)
                filters = butil.prepare_filters(inputs)
                sig, scale = butil.aggregate(idf, filters=filters, **{ind_comp['args']})
                sig = f'{{float(f"{{sig:.3g}}"):g}}'
                return f"{{sig}} {{scale}}{ind_comp.get("unit", "")}"
                """

            self.callbacks[cid] = {
                "provides": ["children"],
                "name": callback_name,
                "code": codeutil.format_code(callback_code),
            }

            blocks.append([[comp]])

        block_size = {"ideal": [2, 1.5], "min": [1, 1]}
        return self._align(blocks, vertical, block_size)

    def ranking(self, gid, dataid, nformat=None, **kwargs):
        id_dict = {"name": f"ranking", **gid}
        label = f"Top items"
        kwargs = {"Div.style": {"textAlign": "left"}, **kwargs}
        div_id, div = bc.div(id_dict, label=label, **kwargs)

        # TODO Universal formatting is a pain, but see what we can do to improve this
        nformat = ".7g"

        # TODO Weigh in on whether using "geo" is the best 'key' (9L down) default
        callback_name = f"{gid['pageid']}_{gid['bankid']}__update_ranking"
        callback_code = f"""
            idf = data["{dataid}"]["df"]
            inputs = dictutil.process_inputs(dash.callback_context.inputs)

            filters = butil.prepare_filters(inputs)
            fdf = butil.filter_df(idf, filters=filters)
            children = []

            column = dictutil.extract_unique("_column", inputs)
            key = dictutil.extract_unique("geo", inputs)
            inputs.update({{"key": key, "column": column}})
            inputs.update({kwargs})

            for item in butil.rank(fdf, **inputs):
                text = f"{{item[1]:{nformat}}}     {{item[0]}}"
                children.extend([html.Span(text), html.Hr()])
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

    def filter_set(self, gid, dataid, columns=(), vertical=False, **kwargs):
        columns = columns or self.data[dataid]["keys"]
        blocks = []
        for col in columns:
            id_dict = {"name": f"{col}_filter", **gid}
            label = f"Select {col}".title()
            option_args = dictutil.extract_path(f"{col}.", kwargs)
            options = {
                "options": list(self.data[dataid]["df"][col].unique()),
                "default": [],
                "overflow": f"""list(data["{dataid}"]["df"]["{col}"].unique())""",
                **option_args,
            }
            cargs = {"Dropdown.multi": True, **kwargs}
            drop_id, dropdown = bc.dropdown(id_dict, options, label=label, **cargs)
            self.outputs[drop_id] = "value"
            blocks.append([[dropdown]])

        # TODO Implement logical combinations once analytics treatment finished
        # if len(columns) >= 2:
        #     id_dict = {"name": f"filter_logic", **gid}
        #     cargs = {"Dropdown.clearable": False, **kwargs}
        #     options = {"options": ["And", "Or"], "default": "Or"}
        #     drop_id, dropdown = bc.dropdown(id_dict, options, label=None, **cargs)
        #     self.outputs[drop_id] = "value"
        #     blocks.append([[dropdown]])

        block_size = {"ideal": [2, 3], "min": [1, 2]}
        return self._align(blocks, vertical, block_size)

    def option_set(self, gid, components, vertical=True, **kwargs):
        blocks = []
        for comp in components:
            id_dict = {"name": comp["name"], **gid}
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

    def fit_controls(self, gid, dataid, vertical=False, **kwargs):
        blocks = []
        # Create the fit function dropdown
        id_dict = {"name": "fitfunc", **gid}
        options = ["linear", "quadratic"]
        label = "Fit Function"
        kwargs = {"Dropdown.clearable": False}
        fit_id, fit_comp = bc.dropdown(id_dict, options, label=label, **kwargs)
        self.outputs[fit_id] = "value"
        # Create the slider that sets training & prediction range
        id_dict = {"name": "fitrange", **gid}
        label = "Fit/Predict range: points to use, points to forecast"
        cid, fit_range = bc.range_slider(id_dict, options, label=label)
        self.outputs[cid] = "value"
        blocks.append([[fit_comp], [fit_range]])

        block_size = {"ideal": [2, 4], "min": [1, 2]}
        return self._align(blocks, vertical, block_size)

    def style_controls(self, gid, dataid, variants=(), vertical=False, **kwargs):
        blocks = []

        # A dropdown to select the line mode
        id_dict = {"name": "mode", **gid}
        options = ["lines+markers", "lines", "markers"]
        kwargs = {"Dropdown.clearable": False}
        mode_id, line_mode = bc.dropdown(id_dict, options, "Mode", **kwargs)
        self.outputs[mode_id] = "value"

        top_row = []
        if variants:
            id_dict = {"name": "variant", **gid}
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

            callback_name = f"{gid['pageid']}_{gid['bankid']}__update_mode"
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
        id_dict = {"name": "marker_size", **gid}
        cid, marker_size = bc.slider(id_dict, sizes, "Marker Size", value=10, **kwargs)
        self.outputs[cid] = "value"
        sizes = pd.Series([1, 10])
        id_dict = {"name": "line_width", **gid}
        cid, line_width = bc.slider(id_dict, sizes, "Line Width", **kwargs)
        self.outputs[cid] = "value"
        bottom_row = [marker_size, line_width]

        block_size = {"ideal": [2, 4], "min": [1, 2]}
        blocks = [[top_row, bottom_row]]
        return self._align(blocks, vertical, block_size)

    def data_table(self, gid, dataid, vertical=True, **kwargs):
        id_dict = {"name": "columns", **gid}
        label = f"{dataid.upper()}: Choose Columns To Show"
        option_args = dictutil.extract(r"^options$|^default$", kwargs)
        options = {
            "options": self.data[dataid]["columns"] + self.data[dataid]["keys"],
            "default": self.data[dataid]["columns"][:3],
            **option_args,
        }
        kwargs = {"Dropdown.multi": True}
        drop_id, dropdown = bc.dropdown(id_dict, options, label=label, **kwargs)
        self.outputs[drop_id] = "value"

        id_dict = {"name": "table", **gid}
        table_id, datatable = bc.table(id_dict, label=None, **kwargs)

        # Columns displayed in the data table are selected here
        self.connectors[table_id] = {
            "inputs": [(drop_id, "value")],
            "outputs": [(table_id, "columns"), (table_id, "data")],
        }

        callback_name = f"{gid['pageid']}_{gid['bankid']}__update_table"
        callback_code = f"""
            fdf = data["{dataid}"]["df"]
            # Default inputs will be anything passed in 'args' of component
            inputs = {kwargs}

            # Override the default inputs with anything from the callback
            inputs.update(dictutil.process_inputs(dash.callback_context.inputs))
            dropdown_cols = dictutil.extract_unique("columns", inputs)

            # Use only first 1000 rows for performance
            fdf = fdf[:1000]
            columns = [{{"name": item, "id": item}} for item in dropdown_cols]
            return [columns, fdf.to_dict('records')]
            """

        self.callbacks[table_id] = {
            "provides": ["columns", "data"],
            "name": callback_name,
            "code": codeutil.format_code(callback_code),
        }

        block_size = {"ideal": [8, 12], "min": [4, 6]}
        blocks = [[[dropdown], [datatable]]]
        return self._align(blocks, vertical, block_size)

    # @logutil.loginfo(level='debug')
    def graph(self, gid, dataid, category="normal", vertical=False, **kwargs):
        id_dict = {"name": "graph", **gid}
        cid, component = bc.graph(id_dict, **kwargs)

        # Set dependent variable based on the type of graph
        if category == "map":
            dep_var = "z"
        else:
            dep_var = "y"

        callback_name = f"{gid['pageid']}_{gid['bankid']}__update_figure"
        callback_code = f"""
            fdf = data["{dataid}"]["df"]
            # NOTE Thinking this through
            # Default inputs will be anything passed in 'args' of component
            # inputs = {kwargs}
            inputs = {{}}

            # Override the default inputs with anything from the callback
            inputs.update(dictutil.process_inputs(dash.callback_context.inputs))

            # NOTE At least in some cases we want a manual override
            inputs.update({kwargs})

            filters = butil.prepare_filters(inputs)
            transforms = butil.prepare_transforms(inputs, dep_var="{dep_var}")
            figure = Graph.{category}(fdf,
                filters=filters,
                transforms=transforms,
                **inputs)
            figure.update_layout(classes.graph)
            style={{'visibility': 'visible'}}
            return figure, style
            """

        self.callbacks[cid] = {
            "provides": ["figure", "style"],
            "name": callback_name,
            "code": codeutil.format_code(callback_code),
        }
        block_size = {"ideal": [8, 12], "min": [4, 4]}
        blocks = [[[component]]]
        return self._align(blocks, vertical, block_size)

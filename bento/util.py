import pandas as pd
import numpy as np
import math
import plotly.express as px

from collections import defaultdict
from bento.common import logger, logutil, dictutil  # noqa

logging = logger.fancy_logger(__name__)


def desnake(text):
    """Turns underscores into spaces"""
    return text.strip().replace("_", " ")


def titlize(text):
    return desnake(text.title())


def get_unit(num):
    scale = ["f", "n", "u", "m", "", "K", "M", "G", "T", "P"]
    offset = 4
    try:
        exp = min(9, offset + math.log10(num) / 3)
        if exp < 0:
            return num, ""
        exp = int(exp)
        sig = round(num / 10 ** ((exp - 4) * 3), 2)
        return sig, scale[exp]
    except Exception:
        return num, ""


# @logutil.loginfo(level="debug")
def prepare_transforms(inputs, dep_var="y"):
    transforms = []
    dep_column = dictutil.extract_unique(f"{dep_var}_column", inputs, pop=False)
    for key, value in dictutil.extract("_transform", inputs, pop=False).items():
        if not value:
            continue
        if "window" in key:
            transforms.append((dep_column, ["rolling", "mean"], [(value,), ()]))
        elif "calc" in key:
            if value == "Rate":
                transforms.append((dep_column, ["diff"], [()]))
            elif value == "Acceleration":
                transforms.append((dep_column, ["diff", "diff"], [(), ()]))
            elif value == "Cumulative":
                transforms.append((dep_column, ["cumsum"], [()]))
        elif "norm" in key:
            if value == "Max":
                transforms.append((dep_column, ["div"], [("trace.max",)]))
            elif value == "Other Series":
                transforms.append((dep_column, ["div"], [("ref.0",)]))

    return transforms


# @logutil.loginfo(level="debug")
def prepare_filters(inputs):
    filters = defaultdict(lambda: defaultdict(list))
    logic = dictutil.extract_unique("filter_logic", inputs, default="or").lower()
    for key, values in dictutil.extract("_filter", inputs, pop=False).items():
        col = key.replace("_filter", "")
        if not values:
            continue
        if not isinstance(values, list):
            values = [values]
        if "date" in key and len(values) == 2:
            filters["between"][col].extend(values)
        else:
            filters[logic][col].extend(values)
    return filters


# NOTE Currently used for pie charts and ranking
# @logutil.loginfo(level='debug')
def filter_df(idf, filters):
    odf = idf
    for logic, columns in filters.items():
        for column, values in columns.items():
            if "datetime" in str(type(values[0])):
                values = [np.datetime64(item) for item in values]
            if logic == "between":
                odf = odf[(odf[column] >= values[0]) & (odf[column] <= values[1])]
            elif logic == "or":
                odf = odf[odf[column].isin(values)]
            elif logic == "and":
                odf = odf[odf[column].isin(values)]

    return odf


def rank(idf, key, column, count=10, **kwargs):
    fdf = idf.groupby([key]).sum().reset_index()
    fdf = fdf.nlargest(count, column)
    return zip(fdf[key], fdf[column])


# NOTE Used for preparing the traces for graphs
# TODO Should combine this with filter_df/
# @logutil.loginfo(level='debug')
def prepare_traces(idf, filters, key_columns):
    # NOTE Brought over from figure callback, default multi-column approach
    # TODO Figure out how to determine default columns from df
    # column = self.data.get("keys", self.data["columns"][0])[0]
    # def_x_column = self.data["columns"][1]
    # idf.groupby(column).max().reset_index().nlargest(8, def_x_column)[column]
    idf["label"] = ""
    idf.name = ""
    traces = [idf]
    for logic, columns in filters.items():
        new_traces = []
        if logic == "between":
            for column, values in columns.items():
                for df in traces:
                    new = df[(df[column] >= values[0]) & (df[column] <= values[1])]
                    new.name = df.name
                    new_traces.append(new)
        elif logic == "or":
            for column, values in columns.items():
                for df in traces:
                    for value in values:
                        new = df[df[column] == value]
                        new.name = df.name
                        try:
                            new.name += " " + value
                        except Exception:
                            # try:
                            new.name += " " + pd.to_datetime(value).strftime("%Y-%m-%d")
                            # except Exception:
                            #     logging.warning(f"Can't add {column} to trace name")
                        new_traces.append(new)
        elif logic == "and":
            for column, values in columns.items():
                for df in traces:
                    for value in values:
                        new = df[df[column] == value]
                        new.name = df.name
                        try:
                            new.name += " " + value
                        except Exception:
                            # try:
                            new.name += " " + pd.to_datetime(value).strftime("%Y-%m-%d")
                            # except Exception:
                            #     logging.warning(f"Can't add {column} to trace name")
                        new_traces.append(new)

        traces = new_traces

    new_traces = []
    for df in traces:
        new = df.groupby(key_columns).sum().reset_index()
        new.name = df.name
        new_traces.append(new)
    traces = new_traces

    return traces


# @logutil.loginfo(level="debug")
def trace_analytics(traces, transforms):
    for transform in transforms:
        column, operations, arg_list = transform
        for trace in traces:
            buff = trace[column]
            for op, args in zip(operations, arg_list):
                final_args = []
                for arg in args:
                    if "trace" in str(arg):
                        oper = arg.split(".")[-1]
                        final_args.append(getattr(buff, oper)())
                    elif "ref" in str(arg):
                        idx = 0
                        final_args.append(traces[idx][column])
                    else:
                        final_args.append(arg)
                buff = getattr(buff, op)(*final_args)
            trace[column] = buff
    return traces


def aggregate(idf, y_column=None, filters=None, logic="sum", keys=None, **kwargs):
    filters = filters or {}
    filters.update(kwargs.get("fixed_filters", {}))
    # TODO Plenty of work to do cleaning up the data processing utilities like this
    keys = keys or ["date"]
    traces = prepare_traces(idf, filters, keys)
    agg_df = pd.concat(traces)

    # NOTE Pay attention to this block for multi-axis support
    if not y_column:
        return len(agg_df), ""
    elif isinstance(y_column, list):
        y_column = y_column[0]
    quantity = getattr(agg_df[y_column], logic)()
    return get_unit(quantity)


def _date_marks(ordered):
    spacing = 7
    style = {}
    labels = {item: pd.Timestamp(item).date().day for item in ordered[::spacing]}
    marks = {
        int(key): {"label": label, "style": style} for key, label in labels.items()
    }
    return marks


def gen_marks(series, variant="auto"):
    """Processes a dataframe column into a valid slider series"""
    ordered = sorted(series)
    spacing = math.ceil(len(ordered) / 10)
    if variant == "date":
        marks = _date_marks(ordered)
    else:
        marks = {item: str(item) for item in series[::spacing]}
    return marks


def gen_options(option_input):
    # In this case, we're given just the set of options only, assuming first is default
    if isinstance(option_input, list):
        option_list = option_input
        default = option_list[0]
    # The default may be specified in the dict version
    elif isinstance(option_input, dict):
        # TODO Make this more robust
        if "value" in option_input:
            return option_input
        option_list = option_input["options"]
        default = option_input.get("default", option_list[0])
    # TODO Can we determine when we should run desnake on the entries?
    options = [{"label": desnake(item).title(), "value": item} for item in option_list]
    return {"options": options, "value": default}


def get_first_numeric(data_types):
    for dtype in data_types:
        if "log" in data_types[dtype]:
            return dtype


def log_color_scale(name, base=2.718, category="sequential"):
    color_category = getattr(px.colors, category)
    color_sequence = getattr(color_category, name)
    # print(color_sequence)
    log_val = [round(1 / base ** idx, 10) for idx in range(len(color_sequence))][::-1]
    log_val[0] = 0
    log_sequence = list(zip(log_val, color_sequence))
    return log_sequence


# @logutil.loginfo(level='debug')
def data_range(pd_df_list, column, scale="category"):
    minimum = pd_df_list[0][column].min()
    maximum = pd_df_list[0][column].max()
    for df in pd_df_list:
        series = df[column]
        minimum = min(minimum, series.min())
        maximum = max(maximum, series.max())
        if scale == "log":
            minimum = max(0.1, minimum)
            minimum = np.floor(max(-1, np.log10(minimum)))
            maximum = np.ceil(np.log10(maximum))
        elif scale == "linear":
            minimum = np.floor(minimum)
            maximum = np.ceil(maximum)
    return [minimum, maximum]


if __name__ == "__main__":

    log_color_scale("Viridis", base=10)

    for i in range(-18, 19):
        unit = "Hz"
        sig, scale = get_unit(10 ** i)
        print(f"{sig} {scale}{unit}")

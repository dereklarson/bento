from bento import Bank
from bento.common import logger, logutil, dictutil  # noqa

logging = logger.fancy_logger(__name__)


class ranking(Bank):
    """Shows an ordered list of a chosen key and metric

    Initialization Parameters
    -------------------------
    nformat: str
        Format string used when displaying the metric text.

    Attributes
    ----------

    Examples
    --------
    """

    # @logutil.loginfo(level="debug")
    def __init__(self, nformat="0.7g", **kwargs):
        block_size = {"ideal": [4, 2], "min": [1, 1]}

        super().__init__(**kwargs)

        # Set default styling attributes for the text
        # TODO Find what good defaults are and allow overrides
        args = {
            "label": None,
            "Div.style": {
                "textAlign": "left",
                # "lineHeight": 1.2,
                # "fontStyle": "italic",
            },
        }
        # TODO Combining args from defaults, descriptor, and other banks needs real help
        cb_args = dictutil.extract("^key$|^text_key$|^column$", kwargs)
        cb_code = f"""
            inputs = dictutil.strip_attr(inputs)
            filters = butil.prepare_filters(inputs)
            fdf = butil.filter_df(sdf, filters=filters)

            column = dictutil.extract_unique("_column", inputs)
            geo = dictutil.extract_unique("geo", inputs)
            inputs.update({{"key": [geo, "fips"], "text_key": geo, "column": column}})
            inputs.update(**{cb_args})

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

        div = self.create_component("div", name="ranking", args=args)
        cb_outputs = [(div.uid, "children")]
        self.add_callback(div.uid, cb_outputs, cb_code)
        self.align(block_size)

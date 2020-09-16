from bento import Bank
from bento.common import logger, logutil, dictutil  # noqa

logging = logger.fancy_logger(__name__)


class text_box(Bank):
    """Simply displays text, potentially reactive to other toggles

    Initialization Parameters
    -------------------------
    text: str
        Static text to display. This will be overridden if connected to a bank
        that supplies new text.

    Attributes
    ----------

    Examples
    --------
    """

    # @logutil.loginfo(level="debug")
    def __init__(self, text="<info>", cb_field="column", **kwargs):
        block_size = {"ideal": [2, 4], "min": [1, 1]}

        super().__init__(**kwargs)

        # Set default styling attributes for the text
        # TODO Find what good defaults are and allow overrides
        args = {
            "children": text,
            "label": None,
            "Div.style": {
                "textAlign": "left",
                "lineHeight": 1.2,
                "fontStyle": "italic",
            },
        }
        # Static version of the text box
        if isinstance(text, str):
            self.create_component("div", name="text", args=args)
        # Dynamic version with a dictionary of options
        elif isinstance(text, dict):
            default = text.get("default", "<default>")
            args["children"] = default
            cb_code = f"""
                field = dictutil.extract_unique("{cb_field}", inputs)
                text = {text}
                return text.get(field, "{default}")
            """
            div = self.create_component("div", name="text", args=args)
            cb_outputs = [(div.uid, "children")]
            self.add_callback(div.uid, cb_outputs, cb_code)

        self.align(block_size)

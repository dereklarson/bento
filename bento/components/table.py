from bento import Component
from bento.common import logger, logutil, dictutil  # noqa

logging = logger.fancy_logger(__name__)


class table(Component):
    def __init__(self, **kwargs):
        args = {
            "page_action": "none",
            "filter_action": "native",
            "sort_action": "native",
            "style_table": {
                "overflowX": "auto",
                "overflowY": "auto",
                "height": "300px",
            },
            # NOTE This is needed until Plotly fixes name collision with Bootstrap Grid css
            "css": [
                {"selector": ".row-1", "rule": "margin-right: 0px; margin-left: 0px"},
            ],
        }
        super().__init__("dash_table", "DataTable", args, **kwargs)

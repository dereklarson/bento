import pandas as pd

from bento import Bank
from bento.common import logutil  # noqa


class option_set(Bank):
    """

    Initialization Parameters
    -------------------------

    Attributes
    ----------

    Examples
    --------
    """

    # @logutil.loginfo(level="debug")
    def __init__(self, components, **kwargs):
        block_size = {"ideal": [3, 2], "min": [1, 1]}
        super().__init__(**kwargs)

        for opt_comp in components:
            # Default to dropdown
            ctype = "dropdown"
            options = opt_comp["options"]
            if len(opt_comp["options"]) <= 3:
                ctype = "selection_list"
            elif isinstance(opt_comp["options"][0], (int, float)):
                ctype = "slider"
                options = pd.Series(opt_comp["options"])
            args = {
                "label": opt_comp["label"],
                "multi": opt_comp.get("multi", False),
                "options": options,
                "Dropdown.clearable": False,
                "RadioItems.labelStyle": {"display": "block"},
                "Checklist.labelStyle": {"display": "block"},
            }
            self.create_component(ctype, opt_comp["name"], args=args)

        self.align(block_size)

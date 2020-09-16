from bento import Bank
from bento.common import logger, logutil, dictutil  # noqa
import numpy as np
import pandas as pd

logging = logger.fancy_logger(__name__)


class selector(Bank):
    """Provides means to set a date or date interval interactively

    Initialization Parameters
    -------------------------
    window: bool
        Whether to include the windowing component or not
    normalization: bool
        Whether to include the normalization component or not
    calculus: bool
        Whether to include the calculus (rates, sums) component or not

    Attributes
    ----------

    Examples
    --------
    """

    # @logutil.loginfo(level="debug")
    def __init__(self, columns=(), **kwargs):
        # NOTE Can be altered to provide a better sizing for the bank
        block_size = {"ideal": [2, 3], "min": [1, 2]}
        super().__init__(**kwargs)

        columns = columns or self.data["keys"]

        for col in columns:
            option_args = dictutil.extract_path(f"{col}.", kwargs)
            option_vals = pd.Series(sorted(self.df[col].unique()))
            options_numeric = np.issubdtype(option_vals, np.number)
            options = {
                "options": list(option_vals),
                "default": [],
                "overflow": f"""
                    list(_global_data["{self.dataid}"]["df"]["{col}"].unique())""",
                **option_args,
            }

            # Default to a dropdown
            comp_type = "dropdown"
            args = {
                "Dropdown.multi": True,
                "label": f"Select {col}".title(),
                "marks": True,
            }
            # If there are 3 or fewer options, go for radio buttons
            if not options_numeric and len(options["options"]) <= 3:
                comp_type = "radio"
            # If there are numerics, use a slider
            elif options_numeric:
                comp_type = "slider"
                options = option_vals
                args["variant"] = "range"
            args["options"] = options
            self.create_component(comp_type, name=f"{col}_filter", args=args)

        self.align(block_size)

        # TODO Implement logical combinations once analytics treatment finished
        # if len(columns) >= 2:
        #     id_dict = {"name": f"filter_logic", **uid}
        #     cargs = {"Dropdown.clearable": False, **kwargs}
        #     options = {"options": ["And", "Or"], "default": "Or"}
        #     drop_id, dropdown = bc.dropdown(id_dict, options, label=None, **cargs)
        #     self.outputs[drop_id] = "value"
        #     blocks.append([[dropdown]])

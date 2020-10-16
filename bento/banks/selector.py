from bento import Bank
from bento.common import logger, logutil, dictutil  # noqa
import numpy as np
import pandas as pd

logging = logger.fancy_logger(__name__)


class selector(Bank):
    """Creates data filters that determine the traces, based on categorical columns.

    Initialization Parameters
    -------------------------
    columns: tuple
        The set of columns from the dataframe that will be used in selection. If this
        isn't specified in the descriptor, the columns used will default to those
        listed as keys in the descriptor.

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

        # TODO Try to meld this with what happens in the option_set bank
        # (e.g. a util function or a class method of option_set)
        for col in columns:
            option_args = dictutil.extract_path(f"{col}.", kwargs)
            option_vals = pd.Series(sorted(self.df[col].unique()))
            options_numeric = np.issubdtype(option_vals, np.number)
            options = {
                "options": list(option_vals),
                "overflow": f"""
                    list(_global_data["{self.dataid}"]["df"]["{col}"].unique())""",
                **option_args,
            }

            # Default to a dropdown
            comp_type = "dropdown"
            args = {
                "label": f"Select {col}".title(),
                "marks": True,
                "multi": True,
                "Dropdown.multi": True,
                "RadioItems.labelStyle": {"display": "block"},
                "Checklist.labelStyle": {"display": "block"},
            }
            if len(options["options"]) <= 3:  # Use a list for few options
                comp_type = "selection_list"
            elif options_numeric:  # If there are numerics, use a slider
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

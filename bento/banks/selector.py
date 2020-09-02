from bento import Bank
from bento.common import dictutil
import bento.components as bc


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

    def __init__(self, columns=(), **kwargs):
        # NOTE Can be altered to provide a better sizing for the bank
        block_size = {"ideal": [2, 3], "min": [1, 2]}
        super().__init__(**kwargs)

        columns = columns or self.data["keys"]

        blocks = []
        for col in columns:
            id_dict = {"name": f"{col}_filter", **self.uid}
            label = f"Select {col}".title()
            option_args = dictutil.extract_path(f"{col}.", kwargs)
            options = {
                "options": list(self.df[col].unique()),
                "default": [],
                "overflow": f"""
                    list(_global_data["{self.dataid}"]["df"]["{col}"].unique())""",
                **option_args,
            }
            # TODO Perhaps use this pattern more broadly, to ensure kwargs unchanged
            cargs = {"Dropdown.multi": True, **kwargs}
            drop_id, dropdown = bc.dropdown(id_dict, options, label=label, **cargs)
            self.outputs[drop_id] = "value"
            blocks.append([[dropdown]])

        # TODO Implement logical combinations once analytics treatment finished
        # if len(columns) >= 2:
        #     id_dict = {"name": f"filter_logic", **uid}
        #     cargs = {"Dropdown.clearable": False, **kwargs}
        #     options = {"options": ["And", "Or"], "default": "Or"}
        #     drop_id, dropdown = bc.dropdown(id_dict, options, label=None, **cargs)
        #     self.outputs[drop_id] = "value"
        #     blocks.append([[dropdown]])

        self._align(blocks, block_size)

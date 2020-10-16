from bento import Bank
from bento.common import dictutil


class axis_controls(Bank):
    """Provides means to set a date or date interval interactively

    Initialization Parameters
    -------------------------
    axes: tuple
        Which axes to have controls for
    multi: tuple
        The axes for which multiple selection is allowed
    scale: bool
        Whether to include a scale radio button selector (linear, log)

    Attributes
    ----------

    Examples
    --------
    """

    # @logutil.loginfo(level='debug')
    def __init__(self, axes=("y"), multi=None, scale=False, **kwargs):
        block_size = {"ideal": [1, 2], "min": [1, 1]}
        super().__init__(**kwargs)

        blocks = []
        for axis_idx, axis in enumerate(axes):
            # Define the dropdown to select a column to display on the axis
            cargs = {"Dropdown.clearable": False, **kwargs}

            if multi and axis in multi:
                cargs["Dropdown.multi"] = True

            default_idx = min(axis_idx, len(self.data["columns"]) - 1)
            option_args = dictutil.extract_path(f"{axis}.", kwargs)
            options = {
                "options": self.data["columns"],
                "default": self.data["columns"][default_idx],
                **option_args,
            }
            args = {"options": options, "label": f"{axis}-Axis Data".title(), **cargs}

            dropdown = self.create_component(
                "dropdown", name=f"{axis}_column", args=args
            )

            if not scale:
                continue

            # Define the radio buttons to select the axis scale
            args = {"options": ["linear", "log"], "multi": False}
            radio = self.create_component(
                "selection_list", name=f"{axis}_scale", args=args
            )

            # TODO includes temporary multi-column support
            callback_code = f"""
                column = dictutil.extract_unique("_column", inputs)

                if isinstance(column, list):
                    column = column[0]

                col_type = data['types'].get(column, 'all')
                options = ["linear", "log", "date"]
                if col_type in (float, int):
                    options = ['linear', 'log']
                elif col_type in ('date', 'datetime'):
                    options = ['date']
                option_dict = butil.gen_options(options)
                return option_dict["options"], option_dict["value"]
            """

            cb_inputs = [(dropdown.uid, "value")]
            cb_outputs = [(radio.uid, "options"), (radio.uid, "value")]
            self.add_internal_callback(radio.uid, cb_inputs, cb_outputs, callback_code)

            blocks.append([[dropdown.definition], [radio.definition]])

        # Override default arrangement
        if scale:
            self.blocks = blocks

        self.align(block_size)

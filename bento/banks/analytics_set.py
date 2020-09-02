from bento import Bank
import bento.components as bc


class analytics_set(Bank):
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

    def __init__(self, window=True, normalize=True, calculus=True, **kwargs):
        # NOTE Can be altered to provide a better sizing for the bank
        block_size = {"ideal": [2, 2], "min": [1, 2]}

        super().__init__(**kwargs)

        blocks = []
        if window:
            id_dict = {"name": "window_transform", **self.uid}
            label = "Averaging Window"
            # TODO Insert calculation of length of time between datapoints
            windows = [(1, "Day"), (7, "Week"), (30, "Month"), (365, "Year")]
            options = {
                "options": [{"value": item[0], "label": item[1]} for item in windows],
                "value": 1,
            }
            kwargs = {"Dropdown.clearable": False}
            window_id, window = bc.dropdown(id_dict, options, label, **kwargs)
            self.outputs[window_id] = "value"
            blocks.append([[window]])

        if normalize:
            id_dict = {"name": f"norm_transform", **self.uid}
            label = f"Normalize by:"
            options = {
                "options": ["None", "Max"],
                "default": "None",
            }
            drop_id, dropdown = bc.dropdown(id_dict, options, label=label, **kwargs)
            self.outputs[drop_id] = "value"
            blocks.append([[dropdown]])

        if calculus:
            id_dict = {"name": f"calc_transform", **self.uid}
            label = f"Sums and Rates"
            options = {
                "options": ["Acceleration", "Rate", "None", "Cumulative"],
                "default": "None",
            }
            drop_id, dropdown = bc.dropdown(id_dict, options, label=label, **kwargs)
            self.outputs[drop_id] = "value"
            blocks.append([[dropdown]])

        self.align(blocks, block_size)

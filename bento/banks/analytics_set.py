from bento import Bank


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

        if window:
            # TODO Insert calculation of length of time between datapoints
            windows = [(1, "Day"), (7, "Week"), (30, "Month"), (365, "Year")]
            options = {
                "options": [{"value": item[0], "label": item[1]} for item in windows],
                "value": 1,
            }
            args = {
                "options": options,
                "label": "Averaging Window",
                "Dropdown.clearable": False,
            }
            self.create_component("dropdown", name="window_transform", args=args)

        if normalize:
            options = {
                "options": ["None", "Max"],
                "default": "None",
            }
            args = {"options": options, "label": "Normalize by:"}
            self.create_component("dropdown", name="norm_transform", args=args)

        if calculus:
            options = {
                "options": ["Acceleration", "Rate", "None", "Cumulative"],
                "default": "None",
            }
            args = {"options": options, "label": "Sums and Rates"}
            self.create_component("dropdown", name="calc_transform", args=args)

        self.align(block_size)

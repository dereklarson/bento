import numpy as np

from bento import Bank
import bento.components as bc


class date_control(Bank):
    """Provides means to set a date or date interval interactively

    Initialization Parameters
    -------------------------
    variant: string -- "single" | "range"
        Whether to have a single handle/picker defining one date, or two
        handles/pickers to define an interval.
    column: string
        The column name from the DataFrame which has the date data
    picker: bool
        Whether to include a date picker or not
    kwargs: dict
        Passthrough of additional arguments that might get picked up at other levels
        such as the super() call.

    Attributes
    ----------

    Examples
    --------
    """

    def __init__(self, variant="single", column="", picker=False, **kwargs):
        # NOTE Can be altered to provide a better sizing for the bank
        block_size = {"ideal": [2, 3], "min": [1, 2]}

        kwargs["variant"] = variant
        super().__init__(**kwargs)

        # TODO Incorporate type-checking and autostructure output
        default = "date" if "date" in self.df.columns else self.data["columns"][0]
        column = column or default

        # Generate the component calls
        label = f"Select {column}:"
        id_dict = {"name": f"{column}_filter", **self.uid}
        series = np.unique(self.df[column])
        slider_id, slider = bc.slider(id_dict, series, label, variant=self.variant)
        self.outputs[slider_id] = "value"

        # Return early if we only have a slider
        if not picker:
            blocks = [[[slider]]]
            self.align(blocks, block_size)
            return

        block_size = {"ideal": [2, 4], "min": [1, 3]}
        id_dict = {"name": f"{column}_picker", **self.uid}
        dt_series = np.unique(self.df[column].dt.to_pydatetime())
        picker_id, picker = bc.date_picker(
            id_dict, dt_series, None, variant=self.variant
        )
        # TODO The code creation needs a better methodology
        if self.variant == "single":
            cb_inputs = [(picker_id, "date")]
            extractor = """
            return numpy.datetime64(dictutil.extract_unique("date", inputs), 'ns')
            """
        elif self.variant == "range":
            cb_inputs = [(picker_id, "start_date"), (picker_id, "end_date")]
            extractor = """
            start = dictutil.extract_unique("start_date", inputs)
            end = dictutil.extract_unique("end_date", inputs)
            ret = [numpy.datetime64(start, 'ns'), numpy.datetime64(end, 'ns')]
            return ret
            """

        cb_outputs = [(slider_id, "value")]
        self.add_internal_callback(slider_id, cb_inputs, cb_outputs, extractor)
        blocks = [[[picker], [slider]]]
        self.align(blocks, block_size)

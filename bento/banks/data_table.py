from bento import Bank
from bento import components as bc
from bento.common import logger, logutil, dictutil  # noqa

logging = logger.fancy_logger(__name__)


class data_table(Bank):
    """Shows the contents of a DataFrame associated with the dataid

    Initialization Parameters
    -------------------------
    rows: int
        Defines how many rows from the dataframe to access. In order to perform
        adequately, this must often be restricted to a smallish number
        (TODO figure out a reasonable estimate)

    Attributes
    ----------

    Examples
    --------
    """

    # @logutil.loginfo(level="debug")
    def __init__(self, rows=1000, **kwargs):
        block_size = {"ideal": [8, 12], "min": [4, 6]}
        super().__init__(**kwargs)

        option_args = dictutil.extract(r"^options$|^default$", kwargs)
        options = {
            "options": self.data["columns"] + self.data["keys"],
            "default": self.data["columns"][:3],
            **option_args,
        }
        default_label = f"{self.dataid.upper()}: Choose Columns To Show"
        dropdown = bc.dropdown(
            id_dict=self.create_id(name="columns"),
            options=options,
            label=default_label,
            **{"Dropdown.multi": True},
        )

        table = bc.table(id_dict=self.create_id(name="table"), label=None, **kwargs)

        # Columns displayed in the data table are selected here

        callback_code = f"""
            dropdown_cols = dictutil.extract_unique("columns", inputs)

            # Slice by the rows argument
            fdf = sdf[:{rows}]

            columns = [{{"name": item, "id": item}} for item in dropdown_cols]
            return [columns, fdf.to_dict('records')]
            """

        self.add_internal_callback(
            target_cid=table.uid,
            cb_inputs=[(dropdown.uid, "value")],
            cb_outputs=[(table.uid, "columns"), (table.uid, "data")],
            code=callback_code,
        )
        self.outputs[dropdown.uid] = "value"

        self.blocks = [[[dropdown.definition], [table.definition]]]
        self.align(block_size)

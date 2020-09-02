""" Bank class
"""
import numpy as np

from bento.common import logger, logutil, codeutil, dictutil  # noqa

logging = logger.fancy_logger(__name__)


class Bank:
    """Packages Dash components to easily arrange, style, and connect them

    Initialization Parameters
    -------------------------
    uid: dict
        Contains the unique page and bank strings as a dictionary.
        e.g. {"page_id": "main", "bank_id": "selector_1"}
    dataid: string
        Defines the dataframe used by this bank. This is accessed from the global
        data variable in the Bento app.
    variant: string
        Many banks have support for variations on the functionality, which would be
        defined here. For example, a `date_control` has a variant "range" which
        means a date picker or slider would have both a start and end date; the
        "normal" variant just has a single date value.
    vertical: bool
        Whether this bank should be arranged vertically or not, in which case the
        components will stack and the shape will adjust.
    kwargs: dict
        Passthrough of additional arguments that might get picked up at other levels.

    Attributes
    ----------
    outputs: dict
    callbacks: dict
    connectors: dict

    Examples
    --------
    The Bank class is mostly meant for private, internal structure
    """

    # @logutil.loginfo(level="debug")
    def __init__(
        self,
        uid,
        g_data,
        dataid="",
        variant="",
        vertical=False,
        height=None,
        width=None,
        **kwargs,
    ):
        self.uid = uid
        self.dataid = dataid

        # Just reference the data we actually need
        self.data = g_data[dataid]
        self.df = g_data[dataid]["df"]
        self.fixed_width = width
        self.fixed_height = height
        self.variant = variant
        self.vertical = vertical

        # Store the kwargs for processing in the callback
        self.kwargs = kwargs

        # The following 2 are defaults to be overwritten later
        self.layout = [[]]
        self.sizing = {"ideal": [2, 2], "min": [1, 1]}

        self.outputs = {}
        self.callbacks = {}
        self.connectors = {}

    # @logutil.loginfo(level='debug')
    def align(self, blocks, block_size):
        if self.vertical:
            self.layout = np.vstack(blocks)
            ideal_height = int(len(blocks) * block_size["ideal"][0])
            min_height = int(len(blocks) * block_size["min"][0])
            self.sizing = {
                "ideal": [ideal_height, block_size["ideal"][1]],
                "min": [min_height, block_size["min"][1]],
            }
        else:
            self.layout = np.hstack(blocks)
            ideal_width = int(len(blocks) * block_size["ideal"][1])
            min_width = int(len(blocks) * block_size["min"][1])
            self.sizing = {
                "ideal": [block_size["ideal"][0], ideal_width],
                "min": [block_size["min"][0], min_width],
            }
        if self.fixed_height:
            self.sizing["ideal"][0] = self.fixed_height
            self.sizing["min"][0] = self.fixed_height
        if self.fixed_width:
            self.sizing["ideal"][1] = self.fixed_width
            self.sizing["min"][1] = self.fixed_width

    def name_callback(self, target_cid):
        """Names callback based on the page, bank, and component being targeted"""
        prefix = f"{self.uid['pageid']}_{self.uid['bankid']}"
        action = f"update_{target_cid.split('|')[-1]}"
        return f"{prefix}__{action}"

    def add_callback(self, target_cid, cb_outputs, code):
        """Adds callback function that can update the component of the bank"""

        input_processing = f"""
            data = _global_data["{self.dataid}"]
            sdf = data["df"]
            inputs = dictutil.strip_prefix(dash.callback_context.inputs)
            inputs.update({self.kwargs})
        """
        callback_code = "\n    ".join([input_processing, code])

        self.callbacks[target_cid] = {
            "provides": [val[1] for val in cb_outputs],
            "name": self.name_callback(target_cid),
            "code": codeutil.format_code(callback_code),
        }

    def add_internal_callback(self, target_cid, cb_inputs, cb_outputs, code):
        """Adds a callback meant to update intra-bank components"""

        # The extra bit is defining up front what inputs the callback takes
        # (this is handled by user-defined inter-bank connections otherwise)
        self.connectors[target_cid] = {
            "inputs": cb_inputs,
            "outputs": cb_outputs,
        }

        self.add_callback(target_cid, cb_outputs, code)

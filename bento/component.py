""" Component class
"""
from bento.common import logger, logutil, dictutil  # noqa

logging = logger.fancy_logger(__name__)


class Component:
    """Contains the information needed to call a Plotly Dash component

    Initialization Parameters
    -------------------------
    dash_lib: str
        The library shorthand within Plotly Dash where the component resides.
        The major options are: dcc, html, dash_table
    dash_component: str
        The Plotly Dash component name. This will generally be capitalized.
    kwargs: dict
        Passthrough of additional arguments that might get picked up at other levels.

    Attributes
    ----------
    uid: str
        Unique identifier for the component
    definition: dict
        This is the set of information used by the Jinja template to create the
        component call.
    output: str
        The name of the attribute where data will be accessible for the component.
        Most often this is "value".

    Examples
    --------
    The Bank class is mostly meant for private, internal structure
    """

    # @logutil.loginfo(level="debug")
    def __init__(
        self,
        dash_lib,
        dash_component,
        internal_args,
        id_dict,
        label=None,
        output="value",
        suffix="",
        **kwargs,
    ):
        bankid, name, pageid = dictutil.pluck(id_dict)
        self.uid = f"{pageid}/{bankid}|{name}{suffix}"
        self.output = output

        self.definition = {
            "lib": dash_lib,
            "component": dash_component,
            "label": label,
            "args": {
                "id": self.uid,
                **internal_args,
                # Allows users to supply arguments to Dash components via the descriptor
                **dictutil.extract_path(f"{dash_component}.", kwargs),
            },
        }

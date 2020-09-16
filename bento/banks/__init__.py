# Import all Bank classes, so we can access them by name on demand
from .analytics_set import analytics_set  # noqa
from .axis_controls import axis_controls  # noqa
from .data_table import data_table  # noqa
from .date_control import date_control  # noqa
from .graph import graph  # noqa
from .indicators import indicators  # noqa
from .ranking import ranking  # noqa
from .selector import selector  # noqa
from .text_box import text_box  # noqa

import sys
import inspect

# Convenience code for tracking banks
_bank_map = {}
for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj):
        _bank_map[name] = obj

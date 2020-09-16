# Import all Bank classes, so we can access them by name on demand
from .html import div, indicator  # noqa
from .display import graph  # noqa
from .selection import date_picker, dropdown, radio, slider  # noqa
from .table import table  # noqa

import sys
import inspect

# Convenience code for tracking banks
_component_map = {}
for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj):
        _component_map[name] = obj

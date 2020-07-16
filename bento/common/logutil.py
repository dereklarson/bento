import flask
import functools
import inspect
import os
import traceback
from bento.common import logger

# logging = logger.fancy_logger(__name__)
# We want to use a simple format here because we care about the wrapped function
# Not the location and name of the wrapper
logging = logger.fancy_logger(__name__, fmt="bare")


def _parse_id(func):
    """Supplies the module name and functon name as a 2-tuple"""
    return (func.__module__.split(".")[-1], func.__name__)


def loginfo(level="debug", log_route=False):
    def inner(func):
        """Wraps class methods to provide automatic log output on args/return value"""
        module, name = _parse_id(func)

        # Retrieves list of ordered arg names from the decorated function
        arg_names = list(inspect.signature(func).parameters.keys())
        class_method = False
        # Removes class-related leading arg from consideration
        if arg_names and arg_names[0] in ("self", "cls"):
            class_method = True
            arg_names = arg_names[1:]

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Look back in the call stack for the appropriate function
            stack_idx = -2
            stack = traceback.extract_stack()
            lineno = stack[stack_idx].lineno
            callFunc = stack[stack_idx].name
            filename = os.path.basename(stack[stack_idx].filename).split(".")[0]
            msg_base = f"{module}.{name} @ {filename}.{callFunc}:{lineno}"

            # Log each argument to the function
            out_args = {}
            start_idx = 0
            if class_method:
                start_idx = 1
            for arg_name, arg_value in zip(arg_names, args[start_idx:]):
                out_args[arg_name] = arg_value
            out_args.update(kwargs)
            msg = f"{msg_base} - Input Arguments:"
            getattr(logging, level)(msg)
            getattr(logging, level)(out_args)

            # The call itself
            result = func(*args, **kwargs)

            # If flagged, also try to log the request object
            if log_route:
                logging.debug(flask.request.json)

            # Similarly log the result of the function
            if type(result) in (dict, list, tuple):
                typename = type(result).__name__
                msg = f"{msg_base} - Returning {typename} of length {len(result)}"
                getattr(logging, level)(msg)
            getattr(logging, level)(result)
            return result

        return wrapper

    return inner

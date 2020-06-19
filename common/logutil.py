import flask
import functools
from common import logger

# logging = logger.fancy_logger(__name__)
# We want to use a simple format here because we care about the wrapped function
# Not the location and name of the wrapper
logging = logger.fancy_logger(__name__, fmt="bare")


def _parse_id(func):
    """Supplies the module name and functon name as a 2-tuple"""
    return (func.__module__.split(".")[-1], func.__name__)


def _log_args(args, kwargs, module, name, logger=None, level="debug"):
    logger = logger or logging
    baseargs = [arg if type(arg) in (str, int, float) else "..." for arg in args]
    getattr(logger, level)(f"{module}.{name} - {baseargs}")
    for arg in args:
        if type(arg) not in (str, int, float):
            getattr(logger, level)(arg)
    if kwargs:
        getattr(logger, level)(kwargs)


def _log_return(result, module, name, logger=None, level="debug"):
    logger = logger or logging
    if type(result) in (dict, list, tuple):
        getattr(logger, level)(f"{module}.{name} - returning {len(result)} items")
        if len(result) < 10:
            getattr(logger, level)(result)


# TODO Can we combine the following 2 wrappers and leveling?
# NOTE try evaluating whether the func is a class method or standalone
def loginfo(logger=None, level="debug"):
    def inner(func):
        """Wraps class methods to provide automatic log output on args/return value"""
        module, name = _parse_id(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Carefully log each argument to the function
            _log_args(args, kwargs, module, name, logger=logger, level=level)

            # The call itself
            result = func(*args, **kwargs)

            # Similarly log the result of the function
            _log_return(result, module, name, logger=logger, level=level)
            return result

        return wrapper

    return inner


def logdebug(func):
    """Wraps class methods to provide automatic log output on args/return value"""
    module, name = _parse_id(func)

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Carefully log each argument to the function
        _log_args(args, kwargs, module, name)

        # The call itself
        result = func(self, *args, **kwargs)

        # Similarly log the result of the function
        _log_return(result, module, name)
        return result

    return wrapper


def logroute(func):
    """Wraps Flask routes to provide automatic log the args/return and request"""
    module, name = _parse_id(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _log_args(args, kwargs, module, name)

        # Also log the request object
        logging.debug(flask.request.json)

        result = func(*args, **kwargs)
        _log_return(result, module, name)
        return result

    return wrapper

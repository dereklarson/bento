import re

from bento.common.logger import fancy_logger

logging = fancy_logger(__name__)


# Destructures a dictionary (vaguely like ES6 for JS)
# NOTE Results are SORTED by key alphabetically, so you must sort your receiving vars
def pluck(input_dictionary):
    items = sorted(input_dictionary.items())
    return [item[1] for item in items]


def _cid2c(cid):
    """Gets just the component portion of a cid string
    e.g. main_page/axis_controls|x_column.value => x_column
    """
    return cid.split("|")[-1].split(".")[0]


def process_inputs(input_dictionary):
    """Alters the keys of a dictionary by a helper function"""
    return {_cid2c(key): val for key, val in input_dictionary.items()}


def extract(regex, input_dictionary, unique=False, pop=True):
    """Splits off a subset dictionary with keys matching the provided 'path' prefix"""
    method = "pop" if pop else "get"
    match_keys = [key for key in input_dictionary if re.search(regex, key)]
    output = {key: getattr(input_dictionary, method)(key) for key in match_keys}

    if unique and len(match_keys) != 1:
        logging.warning(f"Unique extraction of {regex} failed: got {len(match_keys)}")
        logging.warning(input_dictionary)
    elif unique:
        return pluck(output)[0]
    else:
        return output


def extract_path(path, input_dictionary):
    """Splits off a subset dictionary with keys matching the provided 'path' prefix"""
    match_keys = [key for key in input_dictionary if key.startswith(path)]
    output = {key.replace(path, ""): input_dictionary.pop(key) for key in match_keys}
    return output


def merge(d_base, d_in, loc=None):
    """Adds leaves of nested dict d_in to d_base, keeping d_base where overlapping"""
    loc = loc or []
    for key in d_in:
        if key in d_base:
            if isinstance(d_base[key], dict) and isinstance(d_in[key], dict):
                merge(d_base[key], d_in[key], loc + [str(key)])
            elif isinstance(d_base[key], list) and isinstance(d_in[key], list):
                for item in d_in[key]:
                    d_base[key].append(item)
            elif d_base[key] != d_in[key]:
                d_base[key] = d_in[key]
        else:
            d_base[key] = d_in[key]
    return d_base


def common_keys(dict_a, dict_b):
    """Returns new dict with the common keys of the input dicts using dict_a values"""
    return {key: dict_a[key] for key in dict_a.keys() & dict_b.keys()}


class Edict(dict):
    def __init__(self, initial):
        if not hasattr(initial, "__iter__"):
            try:
                # This works fine for dataclasses, it seems
                super().__init__(vars(initial))
            except Exception:
                logging.debug("Failed to ingest into Edict...")
                logging.debug(initial)
        else:
            super().__init__(initial)
        pass

    def __and__(self, other):
        """Returns the first dict with only keys that overlap with the second"""
        return common_keys(self, other)

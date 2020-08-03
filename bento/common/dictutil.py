import re

from bento.common import logutil  # noqa
from bento.common.logger import fancy_logger

logging = fancy_logger(__name__)


def pluck(input_dictionary):
    """Destructures a dictionary (vaguely like ES6 for JS)
       Results are SORTED by key alphabetically! You must sort your receiving vars
    """
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


def extract(regex, input_dictionary, pop=True):
    """Splits off a subset dictionary with keys matching the provided 'path' prefix"""
    method = "pop" if pop else "get"
    match_keys = [key for key in input_dictionary if re.search(regex, key)]
    output = {key: getattr(input_dictionary, method)(key) for key in match_keys}
    return output


def extract_unique(regex, input_dictionary, pop=True, default=None):
    method = "pop" if pop else "get"
    match_keys = [key for key in input_dictionary if re.search(regex, key)]
    output = {key: getattr(input_dictionary, method)(key) for key in match_keys}

    if len(match_keys) > 1:
        logging.warning(f"Regex {regex} not unique: {len(match_keys)} matches")
        logging.warning(input_dictionary)
    elif len(match_keys) == 0:
        return default
    else:
        return pluck(output)[0]


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


# @logutil.loginfo()
def flatten(dict_in, delim="__", loc=[]):
    """Un-nests the dict by combining keys, e.g. {'a': {'b': 1}} -> {'a_b': 1}"""
    loc = loc or []
    output = {}
    if not dict_in and loc:
        output[delim.join(loc)] = {}
    for key in dict_in:
        if isinstance(dict_in[key], dict):
            nest_out = flatten(dict_in[key], delim=delim, loc=loc + [str(key)])
            output.update(nest_out)
        else:
            base_key = delim.join(loc + [str(key)])
            output[base_key] = dict_in[key]
    return output


def nest(dict_in, delim="__"):
    """Nests the input dict by splitting keys (opposite of flatten above)"""
    # We will loop through all keys first, and keep track of any first-level keys
    # that will require a recursive nest call. 'renest' stores these keys
    output, renest = {}, []
    for key in dict_in:
        if delim not in key:
            output[key] = dict_in[key]
            continue
        loc = key.split(delim, 1)
        if loc[0] not in output:
            output[loc[0]] = {}
            # Uniquely add the key to the subdictionary we want to renest
            renest.append(loc[0])
        output[loc[0]][loc[1]] = dict_in[key]

    # Renest all higher-level dictionaries
    for renest_key in renest:
        output[renest_key] = nest(output[renest_key])
    return output


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

    def __and__(self, other):
        """Returns the first dict with only keys that overlap with the second"""
        return common_keys(self, other)

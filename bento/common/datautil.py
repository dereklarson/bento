"""This is a collection of utilities related to loading data from file
"""
import pandas as pd
import pathlib
import pkgutil
from fuzzywuzzy import fuzz

from bento.common import util, logger

logging = logger.fancy_logger(__name__)


def clean_string_name(item):
    return item.strip().replace("*,()", "")


@util.memoize
def fuzzy_search(name, corpus, clean=clean_string_name):
    name = clean(name)
    output = ""
    best = 0
    for item in corpus:
        methods = [fuzz.partial_ratio, fuzz.token_sort_ratio]
        ratio = max([method(clean(item), name) for method in methods])
        if ratio == 100:
            return item
        if ratio > best:
            best = ratio
            output = item
    return output


def df_loader(filename, package="bento", parse_dates=None, location="."):
    args = {
        "parse_dates": parse_dates or [],
        "infer_datetime_format": True,
    }
    # First try locally for an override file, then check assets
    init_py_path = pkgutil.get_loader(package).path
    package_path = pathlib.Path(init_py_path).parent
    location_list = [location, "assets", f"{package_path}/assets"]
    for loc in location_list:
        try:
            logging.debug(f"Searching for {filename} at {loc}")
            df = pd.read_csv(f"{loc}/{filename}", **args)
            return df
        except FileNotFoundError:
            pass

    logging.warning(f"Unable to load {filename} from any of {location_list}")


def autostructure(idf, mods=None):
    dates = [key for key, val in dict(idf.dtypes).items() if "date" in val.__str__()]
    keys = [key for key, val in dict(idf.dtypes).items() if val.__str__() == "object"]
    numeric = {
        key: int if "int" in val.__str__() else float
        for key, val in dict(idf.dtypes).items()
        if key not in dates + keys
    }
    data = {
        "df": idf,
        "dates": dates,
        "keys": keys,
        "columns": list(numeric.keys()),
        "types": numeric,
    }
    return data

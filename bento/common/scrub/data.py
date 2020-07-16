from iso3166 import countries
from fuzzywuzzy import fuzz

from bento.common.util import memoize
from bento.common.logger import fancy_logger

logging = fancy_logger(__name__)


def clean_string_name(item):
    return item.strip().replace("*,", "")


@memoize
def fuzzy_search(name, corpus, clean=clean_string_name):
    name = clean(name)

    output = ""
    best = 0
    for item in corpus:
        item = clean(item)
        methods = [fuzz.partial_ratio, fuzz.token_sort_ratio]
        ratio = max([method(item, name) for method in methods])
        if ratio == 100:
            return item
        if ratio > best:
            best = ratio
            output = item
    return output


def normalize_countries(idf, column="country", corpus=countries):
    inputs = idf[column].unique()
    for country in inputs:
        entry = corpus.get(country, None)
        if not entry:
            reference_list = (country.apolitical_name for country in countries)
            new = fuzzy_search(country, reference_list)
            # logging.info(f"Missing '{country}', assigning '{new}' via fuzzy search")
            logging.debug(f"Missing '{country}', assigning unicode version")
            entry = corpus.get(new)
        idf.loc[idf[column] == country, "alpha3"] = getattr(entry, "alpha3")
        idf.loc[idf[column] == country, column] = entry.apolitical_name

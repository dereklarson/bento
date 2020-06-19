import json
from urllib import request

from common import logger, dictutil  # noqa

logging = logger.fancy_logger(__name__)


geojson = {}
try:
    with open("assets/geojson_us_counties.json", "r") as fh:
        geojson["us_counties"] = json.load(fh)
except Exception:
    try:
        with request.urlopen(
            "https://raw.githubusercontent.com/plotly/"
            "datasets/master/geojson-counties-fips.json"
        ) as response:
            geojson["us_counties"] = json.load(response)
    except Exception:
        logging.warning("Problem loading the US county Geojson from web")

try:
    with open("assets/geojson_us_states.json", "r") as fh:
        geojson["us_states"] = json.load(fh)
except Exception:
    try:
        with request.urlopen(
            "https://raw.githubusercontent.com/PublicaMundi/"
            "MappingAPI/master/data/geojson/us-states.json"
        ) as response:
            geojson["us_states"] = json.load(response)
    except Exception:
        logging.warning("Problem loading the US state Geojson from web")

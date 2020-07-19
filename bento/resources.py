import json
import pathlib
import pkgutil
from urllib import request

from bento.common import logger, dictutil  # noqa

logging = logger.fancy_logger(__name__)

# TODO Generalize resource loading
init_py_path = pkgutil.get_loader("bento").path
package_path = pathlib.Path(init_py_path).parent

geojson = {}
resource_list = [
    ("us_counties", "geojson_us_counties.json"),
    ("us_states", "geojson_us_states.json"),
    ("world", "geojson_world.json"),
]

web_backup = {
    "us_counties": (
        "https://raw.githubusercontent.com/plotly/"
        "datasets/master/geojson-counties-fips.json"
    ),
    "us_states": (
        "https://raw.githubusercontent.com/PublicaMundi/"
        "MappingAPI/master/data/geojson/us-states.json"
    ),
}
location_list = [".", "assets", f"{package_path}/assets"]
for uid, resource in resource_list:
    for loc in location_list:
        try:
            with open(f"{loc}/{resource}", "r") as fh:
                geojson[uid] = json.load(fh)
            logging.info(f"...Loaded {resource}")
            break
        except Exception:
            continue

    if uid in web_backup and uid not in geojson:
        logging.info("   Trying web...")
        try:
            with request.urlopen(web_backup[uid]) as response:
                geojson[uid] = json.load(response)
                logging.info(f"...Loaded {resource} from web")
        except Exception:
            logging.warning(f"   ...Failed to load geojson[{uid}]")

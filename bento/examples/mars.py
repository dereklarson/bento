from bento.common import logger, util

logging = logger.fancy_logger(__name__)


def load():
    filename = "sample_mars_data.csv"
    data = util.loader(filename, parse_date=False)
    data.update(
        {
            "keys": ["region", "city"],
            "types": {"date": "date", "population": int, "energy_consumption": float,},
        }
    )
    return data

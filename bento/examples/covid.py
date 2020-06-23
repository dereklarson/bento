from bento.common import logger, util

logging = logger.fancy_logger(__name__)


def load():
    filename = "sample_covid_data.csv"
    data = util.loader(filename, parse_date=True)
    data.update(
        {
            "keys": ["county", "state", "fips"],
            "types": {"date": "date", "cases": int, "deaths": int,},
        }
    )
    return data

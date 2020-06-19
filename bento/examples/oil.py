from common import logger, util

logging = logger.fancy_logger(__name__)


def load():
    filename = "sample_oilngas_data.csv"
    data = util.loader(filename, parse_date=False)
    data.update(
        {
            "keys": ["county", "type", "status"],
            "types": {
                "date": int,
                "wells": int,
                "water_produced": float,
                "oil_produced": float,
                "gas_produced": float,
            },
        }
    )
    return data

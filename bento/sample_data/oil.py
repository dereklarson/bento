from bento.common import logger, datautil

logging = logger.fancy_logger(__name__)


def load():
    filename = "sample_oilngas_data.csv"
    data = {
        "df": datautil.df_loader(filename, parse_dates=False),
        "keys": ["county", "type", "status"],
        "types": {
            "date": int,
            "wells": int,
            "water_produced": float,
            "oil_produced": float,
            "gas_produced": float,
        },
    }
    return data

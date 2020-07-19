from bento.common import logger, util

logging = logger.fancy_logger(__name__)


def load():
    filename = "sample_mars_data.csv"
    data = {
        "df": util.df_loader(filename, parse_dates=False),
        "keys": ["region", "city"],
        "types": {"date": "date", "population": int, "energy_consumption": float,},
    }
    return data

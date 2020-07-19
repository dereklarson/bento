from bento.common import logger, util

logging = logger.fancy_logger(__name__)


def load():
    filename = "sample_covid_data.csv"
    data = {
        "df": util.df_loader(filename),
        "keys": ["county", "state", "fips"],
        "types": {"date": "date", "cases": int, "deaths": int,},
    }
    return data

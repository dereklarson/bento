from bento.common import logger, datautil

logging = logger.fancy_logger(__name__)


def load():
    filename = "sample_covid_data.csv"
    data = {
        "df": datautil.df_loader(filename, parse_dates=["date"]),
        "keys": ["county", "state", "fips"],
        "types": {"date": "date", "cases": int, "deaths": int,},
    }
    return data

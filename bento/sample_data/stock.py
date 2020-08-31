from bento.common import logger, datautil

logging = logger.fancy_logger(__name__)


def load():
    filename = "sample_stock_data.csv"
    data = {
        "df": datautil.df_loader(filename, parse_dates=["date"]),
        "keys": ["symbol"],
        "types": {
            "open": float,
            "low": float,
            "high": float,
            "close": float,
            "volume": int,
        },
    }
    return data

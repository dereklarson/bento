from bento.common import logger, util

logging = logger.fancy_logger(__name__)


def load():
    filename = "sample_stock_data.csv"
    data = {
        "df": util.df_loader(filename, parse_dates=False),
        "keys": ["date", "symbol"],
        "types": {
            "open": float,
            "low": float,
            "high": float,
            "close": float,
            "volume": int,
        },
    }
    return data

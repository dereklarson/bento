from bento.common import logger, util

logging = logger.fancy_logger(__name__)


def load():
    filename = "sample_stock_data.csv"
    data = util.loader(filename, parse_date=False)
    data.update(
        {
            "keys": ["symbol"],
            "types": {
                "date": "date",
                "symbol": str,
                "open": float,
                "low": float,
                "high": float,
                "close": float,
                "volume": int,
            },
        }
    )
    return data

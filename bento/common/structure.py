"""This file defines the needed paths used within an app. It combines information
supplied by environment variables and yields a convenient interface for file ops.
"""
import glob
import pathlib
import pickle
import pandas as pd

from bento.common import logger
from bento.common.environment import ENV

logging = logger.fancy_logger(__name__)


class PathDef:
    def __init__(self, path, make=False, ext=None):
        if path.startswith("/"):
            self.path = path
        elif path.startswith("~"):
            self.path = path.replace("~", ENV.HOME)
        else:
            self.path = f"{ENV.APP_HOME}/{path}"
        self.ext = ext

        if make:
            pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)

    def glob(self):
        pattern = f"{self.path}/*.{self.ext}"
        return glob.glob(pattern)

    def dump(self, result, filename):
        with open(f"{self.path}/{filename}", "wb") as fh:
            pickle.dump(result, fh)

    def read(self, filename):
        return pd.read_csv(f"{self.path}/{filename}.{self.ext}")


class PathConf:
    build = PathDef(path=ENV.BUILD_DIR)
    data = PathDef(path=ENV.DATA_DIR, ext="csv")
    pycache = PathDef(path=ENV.PYCACHE_DIR, make=True, ext="pkl")
    git = PathDef(path=ENV.ORG_DIR)

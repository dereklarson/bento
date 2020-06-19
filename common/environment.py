import re
import os

from common import logger

logging = logger.fancy_logger(__name__)


def parse_env_file(env_file: str) -> dict:
    """When not running in a container, the env_file won't be injected, so we need to
    process the environemnt variables manually using this function"""
    logging.debug("Adding environment variables:")
    with open(env_file, "r") as fh:
        for line in fh:
            match = re.search(r"([A-Z_]+)=(.*)", line)
            try:
                name, val = match.groups()
                os.environ[name] = val
                logging.debug(f"  {name}: {val}")
            except AttributeError:
                pass

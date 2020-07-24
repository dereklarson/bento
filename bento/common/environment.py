"""This is an attempt to structure the ingesting of environment variables.
All used env variables should be in ENV_SPEC and the ENV export be used globally.
Generally, a docker-compose run would be supplying values for most of these. If the
run is outside of Docker, many of these attributes would fall to the defaults.
"""
import os
import re
from dataclasses import dataclass

from bento.common import logger
from bento.common.dictutil import Edict  # Allows set "&" syntax on dict keys

logging = logger.fancy_logger(__name__)


@dataclass
class ENV_SPEC:
    # Generic
    DEV: bool = False
    HOME: str = "."
    APP: str = ""
    APP_HOME: str = "."

    # Organization configuration
    REGISTRY: str = ""

    ORG_DIR: str = "repositories"
    STORAGE_DIR: str = "storage"

    # Python generic variables
    PYCACHE_DIR: str = ".cache"
    ASSETS_DIR: str = "assets"
    DATA_DIR: str = "data"

    # Specifying the build environment for Aleph
    BUILD_DIR: str = "storage/shared"
    DOCKER_PREFIX: str = "aleph__"

    PIPELINE_TECH: str = "beam"

    # Bento specific variables
    BENTO_PORT: int = 7777
    BENTO_DESCRIPTOR: str = "bento.demo_descriptor"
    REFRESH_HOURS: int = 2


def parse_env_file(env_file: str) -> dict:
    """When not running in a container, the env_file won't be injected, so we need to
    process the environemnt variables manually using this function"""
    logging.debug("Adding environment variables:")
    with open(env_file, "r") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            match = re.search(r"([A-Z_]+)=(.*)", line)
            try:
                name, val = match.groups()
                os.environ[name] = val
                logging.debug(f"  {name}: {val}")
            except AttributeError:
                pass


# TODO Enhance once structure is finished
# Loads any env files into the enviroment
try:
    parse_env_file("ORG_ENV")
except Exception:
    pass
# try:
#     parse_env_file("LOCAL_ENV")
# except Exception:
#     pass
# Get all environment variables that are part of the dataclass
ENV = ENV_SPEC(**(Edict(os.environ) & Edict(ENV_SPEC())))
# logging.debug("---Environment variables:")
# logging.debug(vars(ENV))

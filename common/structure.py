"""This is an attempt to structure the ingesting of environment variables.
All defined env variables should be here and the ENV export be used globally.
"""
import os
from dataclasses import dataclass

from common import logger
from common.dictutil import Edict

logging = logger.fancy_logger(__name__)


@dataclass
class ENV_SPEC:
    # Generic
    DEV: bool = False

    # Organization configuration
    ORG_PATH: str = "repositories"
    CACHE: str = "cache"
    REGISTRY: str = ""

    # Python generic variables
    PYCACHE_DIR: str = ".cache"
    ASSETS_DIR: str = "assets"

    # Specifying the build environment for Aleph
    BUILD_DIR: str = "cache/shared"
    DOCKER_PREFIX: str = "aleph__"

    PIPELINE_TECH: str = "beam"

    # Bento specific variables
    BENTO_PORT: int = 7777
    DATA_REPO: str = "/app/data"
    REFRESH_HOURS: int = 2


# Get all environment variables that are part of the dataclass
ENV = ENV_SPEC(**(Edict(os.environ) & Edict(ENV_SPEC())))
logging.debug("---Environment variables:")
logging.debug(vars(ENV))


if __name__ == "__main__":
    os.environ["REGISTRY"] = "gcr.io/backend-243722"
    logging.info(f"Loaded environment via {__name__}")
    logging.debug(vars(ENV))

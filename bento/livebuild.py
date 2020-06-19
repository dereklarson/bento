import os

from common.structure import ENV
from common import logger, exceptions

logging = logger.fancy_logger("livebuild")

# Loading the descriptor of the dashboard
# TODO Have this depend on the ENV variables
try:
    from cache.shared.active.generated import app

    logging.info(f"Loading generated dashboard app from shared.active")
except Exception:
    logging.warning("Issue with generated dashboard load, trying to regenerate")
    logging.warning(exceptions.nice_exc())

    try:
        from cache.shared.active import descriptor

        descriptor.generate("cache/shared/active/generated.py", ENV.DATA_REPO)
        from cache.shared.active.generated import app

        logging.info(f"Loading RE-generated dashboard app from shared.active")
    except Exception:
        logging.warning("Couldn't generate new dashboard, falling back to default ")
        logging.warning(exceptions.nice_exc())
        os.environ["LOGLEVEL_NAME"] = "20"
        from bento import default_desc as descriptor

        logging.info(f"Loading bento descriptor from default template")
        descriptor.generate("cache/shared/active/generated.py", ENV.DATA_REPO)
        from bento.generated import app

if __name__ == "__main__":
    logging.info("Starting Live Builder")
    app.run_server(host="0.0.0.0", port=ENV.BENTO_PORT, debug=True)

import traceback

from bento import bento
from bento.common.structure import ENV
from bento.common import logger

logging = logger.fancy_logger("testbuild")

try:
    logging.info(f"Attempting to regenerate dashboard app from shared.active...")
    from cache.shared.active import descriptor

    app_def = bento.Bento(descriptor.descriptor)
    app_def.write("cache/shared/active/generated.py")
    # ENV.DATA_REPO

    from cache.shared.active.generated import app

    logging.info("...Successful")
except Exception:
    print(traceback.format_exc())

if __name__ == "__main__":
    logging.info("Starting Live Builder")
    app.run_server(host="0.0.0.0", port=ENV.BENTO_PORT, debug=True)

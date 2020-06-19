import traceback
from common.structure import ENV
from common import logger
from bento import default_desc, complex_desc
import dash

app = dash.Dash("test")

logging = logger.fancy_logger("test_write")

loc = "cache/shared/active"

try:
    logging.info("%Generating bento descriptor from default template")
    default_desc.generate(f"{loc}/gen_default.py", ENV.DATA_REPO)
    # logging.info("%Generating bento descriptor from complex template")
    # complex_desc.generate(f"{loc}/gen_complex.py", ENV.DATA_REPO)
    # from bento.generated import app
except Exception:
    print(traceback.format_exc())

app.run_server(debug=True)

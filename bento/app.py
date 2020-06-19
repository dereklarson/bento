from apscheduler.schedulers.background import BackgroundScheduler

from common.structure import ENV
from bento import bento
from bento import demo_descriptor as descriptor
from common import logger

logging = logger.fancy_logger(__name__)

logging.info(f"Generating bento app from demo descriptor")
app_def = bento.Bento(descriptor.descriptor)
app_def.write("/app/generated.py")

scheduler = BackgroundScheduler()
# scheduler.add_job(bento.refresh, "interval", hours=int(ENV.REFRESH_HOURS))
scheduler.start()

from generated import app  # noqa

# This is passed to Gunicorn for the production environment
bento_flask = app.server

if __name__ == "__main__":
    try:

        if ENV.DEV:
            app.run(port=ENV.BENTO_PORT, debug=True)
        else:
            app.run(host="0.0.0.0", port=ENV.BENTO_PORT, debug=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

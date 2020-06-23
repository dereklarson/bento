from bento import bento, demo_descriptor
from bento.common import logger

logging = logger.fancy_logger("example_generate")


def main():
    definition = bento.Bento(demo_descriptor.descriptor)
    definition.write("dash_app.py")


if __name__ == "__main__":
    main()

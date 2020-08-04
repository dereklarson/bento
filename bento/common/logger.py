import dataclasses
import logging
import os
import sys

# Use prettyprinter for dataclass formatting
try:
    import prettyprinter as pprint

    # NOTE ipython extra has issue, throwing a warning if installed and log a DF
    # 'ZMQInteractiveShell' object has no attribute 'highlighting_style'
    pprint.install_extras(exclude=["django", "ipython"], warn_on_error=False)

    # Set a fairly aggressive limit to sequence by default
    # This makes printing more similar to pandas truncation, which is nice
    # NOTE However, this doesn't seem to work for big nested structures, so we
    # might still have to apply a limit on total formatted string lines
    # TODO Add a way to bypass sequence length when needed
    pprint.set_default_config(
        style="dark", max_seq_len=20, width=79, ribbon_width=71, depth=None,
    )
except ImportError:
    import pprint

# ANSI codes that will generate colored text
def_color_map = {
    # reset should suffix any use of the other following prefixes
    "reset": "\x1b[0m",
    "brightred": "\x1b[31m",
    "red": "\x1b[31m",
    "green": "\x1b[32m",
    "yellow": "\x1b[33m",
    "blue": "\x1b[34m",
    "magenta": "\x1b[35m",
    "cyan": "\x1b[36m",
    "light_blue": "\x1b[94m",
    "darkgreen": "\x1b[92m",
    "purple": "\x1b[95m",
}

def_level_color = {
    "CRITICAL": "brightred",
    "ERROR": "red",
    "WARNING": "yellow",
    "INFO": "darkgreen",
    "DEBUG": None,
}

# We never truly want infinite output, 1000 lines is probably enough
config = {
    "DEBUG": {"max_lines": 1000},
    "INFO": {"max_lines": 10},
    "default": {"max_lines": 50},
}

formats = {
    "msg": "{msg}",
    "bare": "{level_str}| {msg}",
    "simple": "{level_str}| {name} | {msg}",
    "full": "{level_str}| {name} | {funcName}:{lineno} - {msg}",
}


# The default schema uses simpler logging for info-level logs, as these are
# intended for consumption at all times (non-debugging)
schemas = {
    "default": {"INFO": "simple", "default": "full"},
}


class FancyFormatter(logging.Formatter):
    """Adds colors and structure to a log output"""

    def __init__(self, schema="default", fmt=None, level_color=None):
        super().__init__()

        # The schema will have level-dependent format strings
        self.schema = schemas.get(schema, schemas["default"])

        # Overrides a schema with a constant log message format
        self.fmt = fmt

        # Level colors can also be overridden, if desired
        self.level_color = level_color or def_level_color
        self.color_map = def_color_map

    def color_text(self, text, color=None):
        """Wraps text in a color code"""
        if not color:
            return text
        prefix = self.color_map.get(color, "")
        if not prefix:
            logging.warning(f"{color} not defined in color_map")
        suffix = self.color_map["reset"] if prefix else ""
        return f"{prefix}{text}{suffix}"

    def level_fmt(self, level):
        return self.color_text(f"{level: <8}", self.level_color.get(level))

    def format(self, record):
        """Automatically called when logging a record"""
        # Allows modification of the record attributes
        record_dict = vars(record)

        # Checks for message format in order:  from message, self.fmt, self.schema
        style = record_dict.get("fmt") or self.fmt
        if not style:
            style = self.schema.get(record.levelname, self.schema["default"])

        # Prepare a pretty version of the message
        curr_conf = config.get(record.levelname, config["default"])

        if isinstance(record_dict["msg"], (dict, list, tuple)):
            pretty = pprint.pformat(record_dict["msg"]).strip("'\"")
        elif dataclasses.is_dataclass(record_dict["msg"]):
            pretty = pprint.pformat(record_dict["msg"])
        else:
            pretty = str(record_dict["msg"])
        total_lines = pretty.count("\n")
        if total_lines > curr_conf["max_lines"]:
            lines = pretty.splitlines()
            # TODO Abstract away the lines left after truncation (e.g. the 2's and 4)
            trunc = total_lines - 6
            pretty = "\n".join(lines[:3] + [f"...truncated {trunc} lines"] + lines[-3:])
        record_dict["level_str"] = self.level_fmt(record.levelname)
        record_dict["msg"] = pretty

        # --- Logging macros for doing some special operations ---
        # Uses purple to draw extra attention to the text of the line
        if record_dict["msg"].startswith("#!"):
            record_dict["msg"] = (
                self.color_text(record_dict["msg"][2:], "purple") + "\n"
            )
        # Doesn't add a newline, allowing line continuation
        elif record_dict["msg"].startswith("#^"):
            record_dict["msg"] = record_dict["msg"][2:]
        # Next two Continue previous line by using a logformat with message text only
        # First with green, indicating a desirable result
        elif record_dict["msg"].startswith("#$+"):
            record_dict["msg"] = self.color_text(record_dict["msg"][3:], "green") + "\n"
            style = "msg"
        # Seconde with red, indicating a problem
        elif record_dict["msg"].startswith("#$-"):
            record_dict["msg"] = self.color_text(record_dict["msg"][3:], "red") + "\n"
            style = "msg"
        else:
            record_dict["msg"] += "\n"
        message = formats[style].format(**record_dict)
        return message


def fancy_logger(name, fmt=None, level=None):
    env_level = os.environ.get("LOGLEVEL_NAME") or os.environ.get("LOGLEVEL")
    if not level:
        level = int(env_level) if env_level else logging.INFO
    name_logger = logging.getLogger(name)
    name_logger.setLevel(level)
    name_logger.propagate = False
    # Make sure not to re-add the handlers if the same name is used
    if not name_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.terminator = ""
        handler.setFormatter(FancyFormatter(fmt=fmt))
        name_logger.addHandler(handler)
    return name_logger


if __name__ == "__main__":
    fl = fancy_logger("test")
    for level in ["debug", "info", "warning", "error"]:
        getattr(fl, level)(f"This is a {level} test")

    fl.info("Multi\nLine\nMessage")
    # Test the Macros: continuation, color
    fl.info("#^Continuation...")
    fl.info("#$+ pass")
    fl.info("#^Continuation...")
    fl.info("#$- fail")
    fl.info("#!Purple message")

    # Test other datatypes
    fl.info(
        {
            "title": "This is a pretty dictionary",
            "reasons": ["indentation", "length-checking"],
            "strings": [str(i) * 8 for i in range(15)],
        }
    )

    try:
        from typing import List, Dict

        @dataclasses.dataclass
        class Build:
            command: str
            orders: List[str] = dataclasses.field(default_factory=list)
            request: Dict = dataclasses.field(
                default_factory=lambda: {"url": "gen_build"}
            )

        orders = [
            "Dataclass prettyprint",
            "APT git curl wget",
            "APT build-essential",
            "PIP3 numpy",
            "PIP3 flask GitPython gcp resumable-media",
        ]

        fl.warning(Build(command="1", orders=orders))
    except ImportError:
        pass

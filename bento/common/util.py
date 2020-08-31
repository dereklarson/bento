import re
import subprocess

from bento.common import logger

logging = logger.fancy_logger(__name__)


def id_func(x):
    return x


def desnake(text):
    """Turns underscores into spaces"""
    return text.strip().replace("_", " ")


def snakify(text):
    for char in "()":
        text = text.replace(char, "")
    text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text).strip()
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", text).lower().replace(" ", "_")


def snakify_column_names(df):
    col_map = {col_name: snakify(col_name) for col_name in df.columns}
    return df.rename(columns=col_map)


def nice_command(cmd):
    proc = subprocess.Popen(cmd)
    try:
        logging.info(f"Waiting on {cmd[0]}")
        logging.debug(cmd)
        proc.wait()
    except KeyboardInterrupt:
        logging.info(f"Letting {cmd[0]} clean up...")
        proc.wait()
        logging.info("...Done")


# Runs a supplied shell command, handling output
def logged_command(cmd, output_dir=".logs", shell=False):
    subprocess.run(["mkdir", "-p", output_dir])
    base_cmd = cmd[0]
    logging.info(f"Running command: {cmd}")
    output = ""
    errors = ""
    with open(f"{output_dir}/{base_cmd}_std.log", "w+") as fout:
        with open(f"{output_dir}/{base_cmd}_err.log", "w+") as ferr:
            result = subprocess.run(cmd, stdout=fout, stderr=ferr, shell=shell)
            try:
                fout.seek(0)
                output = fout.read()
                ferr.seek(0)
                errors = ferr.read()
                if errors:
                    logging.debug("Stderr: {}".format(errors))
            except Exception as exc:
                logging.warning("Issue with capturing log output of subprocess")
                logging.info(exc)

    # TODO refactor with dataclass or other?
    cmd_result = {
        "code": result.returncode,
        "out": output,
        "err": errors,
    }
    return cmd_result


# TODO Look at replacing this with functools.lru_cache
# Decorator: makes functions perform better by reusing cached results for same args
def memoize(func):
    cache = func.cache = {}

    def run(*args, **kwargs):
        # NOTE This does break if args contains non-hashable objects like lists
        key = args + tuple(sorted(kwargs.items()))
        if key in cache:
            return cache[key]
        else:
            result = func(*args, **kwargs)
            cache[key] = result
            return result

    return run

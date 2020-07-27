import re

from bento.common import logger

logging = logger.fancy_logger(__name__)


def parse_versions(version_file: str) -> dict:
    versions = {}
    with open(version_file, "r") as fh:
        for line in fh:
            if line.strip().startswith("#"):
                continue
            match = re.search(r"([A-Z]+)_VERSION=(\d+\.\d+\.\d+)", line)
            try:
                name, ver = match.groups()
                versions[name.lower()] = ver
            except AttributeError:
                logging.warning("Line doesn't match env var regex:")
                logging.info(f"    {line}")
    logging.debug(versions)
    return versions


def bump_version(versions: dict, app: str, level: str, revert: bool) -> None:
    index = 0 if level == "major" else 1 if level == "minor" else 2
    before = versions.get(app, "0.0.0")
    parts = before.split(".")
    if revert:
        if level != "major":
            logging.error(f"Can't revert {level}, only patch")
            return
        if int(parts[index]) <= 0:
            logging.error(f"Can't revert {level} on {parts}")
            return
        parts[index] = str(int(parts[index]) - 1)
    else:
        parts[index] = str(int(parts[index]) + 1)
        # Set any lower indices to 0
        for smaller_index in range(2, index, -1):
            parts[smaller_index] = "0"

    versions[app] = ".".join(parts)
    logging.info(f"Updating {app}:{before} to {versions[app]}")


def write_update(versions: dict, version_file: str) -> None:
    with open(version_file, "w") as fh:
        fh.write("# Versions (machine controlled, edit carefully)\n")
        for app, ver in versions.items():
            fh.write(f"{app.upper()}_VERSION={ver}\n")


def get_version(app: str, version_file: str = "_docker/.versions") -> str:
    versions = parse_versions(version_file)
    return versions.get(app, "0.0.0")


def release(
    app: str,
    level: str = "patch",
    revert: bool = False,
    version_file: str = "_docker/.versions",
) -> str:
    versions = parse_versions(version_file)
    bump_version(versions, app, level, revert=revert)
    write_update(versions, version_file)
    return versions[app]


if __name__ == "__main__":
    release("bento", version_file="_docker/.versions")
    release("bento", version_file="_docker/.versions", revert=True)
    release("bento", level="major", version_file="_docker/.versions")
    release("bento", level="major", version_file="_docker/.versions", revert=True)
    release("bento", level="major", version_file="_docker/.versions", revert=True)

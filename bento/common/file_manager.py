import glob
import os
import pathlib
import shutil
import yaml

from bento.common import logger, logutil, dictutil
from bento.common.structure import ENV

logging = logger.fancy_logger(__name__)


# Defines an ordering of keys for our yaml dictionary outputs
class yaml_schema:
    # TODO Grab these from the yaml file themselves?
    # Keys for Aleph yamls
    header = ["config", "operations", "datasets", "location", "type", "uid"]
    # Keys for docker-compose yamls
    header.extend(["version", "services"])
    footer = ["text"]


def dict_presenter(dumper, data):
    header = yaml_schema.header
    footer = yaml_schema.footer
    ordered = [None for i in range(len(header + footer))]
    insertion_index = len(header)
    for key, value in sorted(data.items()):
        if key in header:
            ordered[header.index(key)] = (key, value)
        elif key in footer:
            ordered[insertion_index + footer.index(key)] = (key, value)
        else:
            ordered.insert(insertion_index, (key, value))
            insertion_index += 1

    return dumper.represent_dict(dict(filter(None, ordered)))


# This will ensure multiline strings use block format (|) instead of quoted
def str_presenter(dumper, data):
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(dict, dict_presenter)
yaml.add_representer(str, str_presenter)


class FileManager:
    @classmethod
    def dump(cls, state, path):
        with open(path, "w") as fh:
            yaml.dump(state, fh, sort_keys=False)

    @classmethod
    def load(cls, filepath, filetype="yaml", key=None):
        with open(filepath, "r") as fh:
            if filetype == "yaml":
                if key:
                    return yaml.load(fh, Loader=yaml.Loader)[key]
                return yaml.load(fh, Loader=yaml.Loader)
            elif filetype == "csv":
                definition = {
                    "location": filepath,
                    "filetype": filetype,
                    "size": 0,
                    "schema": [],
                }
                return definition

    @classmethod
    def merge_yaml(cls, filepath1, filepath2, outfile=None, clean=True):
        """Merge filepath2 keys into filepath1, write to outfile"""
        outfile = outfile or filepath1
        combined = dictutil.merge(cls.load(filepath1), cls.load(filepath2))
        if clean:
            cls.remove(filepath1)
            cls.remove(filepath2)
        cls.dump(combined, outfile)

    # Loads all YAML files in path and returns a dictionary of the contents
    @classmethod
    def load_many(cls, path, prefix="", extension="yaml"):
        output = {}
        filetype = extension.replace(".", "")
        if extension and extension[0] != ".":
            extension = f".{extension}"
            # TODO maybe use a standard mapping of extensions to filetypes
        for filename in glob.glob(f"./{path}/{prefix}*{extension}"):
            try:
                baseid = os.path.splitext(os.path.basename(filename))[0].lower()
                entry = cls.load(filename, filetype)
                output[entry.get("uid", baseid)] = entry
            except IOError as exc:
                logging.warning("Couldn't load {}".format(filename))
                logging.info(exc)

        return output

    @classmethod
    def remove(cls, path):
        if path[0] in ("~", "/"):
            logging.error("Use only relative paths for deletion")
            return
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            logging.info(f"When removing, {path} not found")
            return
        except NotADirectoryError:
            os.remove(path)

    @classmethod
    def cache_path(cls, path_list, uid):
        return f"{ENV.STORAGE_DIR}/{'/'.join(path_list)}/{uid}.yaml"

    @classmethod
    @logutil.loginfo(level="debug")
    def remove_content(cls, payload):
        path_list, uid = dictutil.pluck(payload)
        path = cls.cache_path(path_list, uid)
        cls.remove(path)
        return {"path": path}

    @classmethod
    @logutil.loginfo(level="debug")
    def save_content(cls, payload):
        path_list, state, uid = dictutil.pluck(payload)
        state["location"] = path_list[1]
        path = cls.cache_path(path_list, uid)
        cls.dump(state, path)
        return {"path": path}

    @classmethod
    def prepare_env(cls, metadata, wipe=False):
        loc = f"{ENV.BUILD_DIR}/{metadata['name']}"
        logging.info(f"Preparing {metadata}\n{loc}")
        if wipe:
            try:
                cls.remove(loc)
            except NotADirectoryError:
                pass
            except FileNotFoundError:
                pass
        pathlib.Path(loc).mkdir(parents=True, exist_ok=True)
        os.chmod(loc, 0o755)
        return loc

    @classmethod
    def load_state_series(cls, name="tutorial"):
        with open(f"cache/library/tutorials/{name}.yaml", "r") as fh:
            series = yaml.load(fh, Loader=yaml.Loader)["series"]
        return series

from bento.common import logger, dictutil

logging = logger.fancy_logger(__name__)


def create_component_id(id_dict, suffix=""):
    bankid, name, pageid = dictutil.pluck(id_dict)
    return f"{pageid}/{bankid}|{name}{suffix}"

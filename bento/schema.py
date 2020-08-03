# Page and bank ids, are strings of word characters only with length 2+
# No trailing, leading, or double underscores
bento_uid_regex = r"^(?!_|.*_$|.*__.*)[a-z0-9_]{2,}$"

# One or more words separated by a space
words_regex = r"^\w+( \w+)*$"

page_schema = {
    "banks": {
        "type": "dict",
        "required": True,
        "allow_unknown": True,
        "minlength": 1,
        "keysrules": {"type": "string", "regex": bento_uid_regex},
        "valuesrules": {
            "type": "dict",
            "allow_unknown": True,
            "schema": {
                "type": {"type": "string", "required": True, "regex": bento_uid_regex},
                "width": {"type": "integer"},
                "args": {"type": "dict"},
            },
        },
    },
    "connections": {"type": "dict"},
    "dataid": {"type": "string"},
    "layout": {"type": "list"},
    "sidebar": {"type": "list"},
    "title": {"type": "string"},
    "subtitle": {"type": "string"},
}

descriptor_schema = {
    "name": {"type": "string"},
    "theme": {"type": "string", "regex": words_regex},
    "theme_dict": {"type": "dict"},
    "appbar": {
        "type": "dict",
        "schema": {
            "title": {"type": "string"},
            "subtitle": {"type": "string"},
            "image": {"type": "string"},
        },
    },
    "data": {"type": "dict"},
    "pages": {
        "type": "dict",
        "allow_unknown": True,
        "required": True,
        "minlength": 1,
        "keysrules": {"type": "string", "regex": bento_uid_regex},
        "valuesrules": {"type": "dict", "schema": page_schema},
    },
}

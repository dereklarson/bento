import os
import sys
import traceback


def nice_exc():
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = traceback.extract_tb(exc_tb)
    if len(tb) == 1:
        msg = f"{exc_type.__name__} in: {tb[0].line}"
    else:
        first_file = os.path.basename(tb[0].filename)
        msg = "\n".join(
            [
                f"{exc_type} in '{tb[-1].line}'",
                f"    From {first_file}:{tb[0].lineno} -- {tb[0].line}",
            ]
        )
    return msg

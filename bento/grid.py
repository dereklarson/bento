import math

from bento.common import logger, logutil  # noqa

logging = logger.fancy_logger(__name__, level=10)


# @logutil.loginfo(level='debug')
def apply_grid(page):
    gridsize = {"width": 12, "height": 8, "rowstart": 1}
    if page.get("sidebar"):
        gridsize["width"] = 9
        gridsize["rowstart"] = 4
    layout = page.get("layout")
    arr, bout = arrange(page["banks"], layout, gridsize)
    return {
        "layout": arr,
        "banks": bout,
        "sidebar": page.get("sidebar"),
        "intro": page.get("intro"),
        "title": page.get("title", ""),
        "subtitle": page.get("subtitle", ""),
    }


# TODO Figure out where and when we need this
def _rescale_ref(ref_sizes, grid_width=12, def_width=12):
    new_sizes = {}
    for name, val in ref_sizes.items():
        new_width = math.ceil(val[1] * grid_width / def_width)
        new_sizes[name] = [val[0], new_width]
    return new_sizes


# @logutil.loginfo(level='debug')
def arrange(banks, arrangement, grid):
    """Receives an ordered 2-d matrix of items and calculates default positions"""
    # Simply stack banks if there's no other info
    # TODO Implement a "Tetris" layout that packs in components based on size
    if not arrangement:
        arrangement = [[{"bankid": bankid}] for bankid in banks]

    # logging.warning(arrangement)
    banks_out = []
    # Give banks a position if none is supplied
    y_step = int(grid["height"] / len(arrangement))
    for y_idx, arr_row in enumerate(arrangement):
        if not arr_row:
            continue
        curr_y = y_idx * y_step
        x_step = int(grid["width"] / len(arr_row))
        for x_idx, bank in enumerate(arr_row):
            bankid = bank["bankid"]
            curr_x = x_idx * x_step + grid["rowstart"]
            # TODO Decide here
            # ref = _rescale_ref(banks[bankid]["sizing"], grid_width=grid["width"])
            ref = banks[bankid]["sizing"]
            bank.update(
                {
                    "width": ref["ideal"][1],
                    "slack": ref["ideal"][1] - ref["min"][1],
                    "ref": ref,
                    "position": banks[bankid].get("position", [curr_y, curr_x]),
                    "column": curr_x,
                    "row": curr_y,
                }
            )
            bank["slack_frac"] = bank["slack"] / bank["ref"]["min"][1]
            banks_out.append(bank)
        appease(banks, arr_row, grid)
        for bank, r_neighbor in zip(arr_row[:-1], arr_row[1:]):
            r_neighbor["column"] = bank["column"] + bank["width"]
    return arrangement, banks_out


# @logutil.loginfo(level='debug')
def appease(banks, row, grid):
    """Trims rows until they fit inside the grid, if possible"""
    # Add up the total width allocated for the row
    total_width = row[-1]["width"]
    total_slack = row[-1]["slack"]
    for bank, neighbor in zip(row[:-1], row[1:]):
        total_width += bank["width"]
        total_slack += bank["slack"]

    # Iterate through
    diff = grid["width"] - total_width
    while diff < 0 and total_slack > 0:
        ordered = sorted(row, key=lambda x: x["slack_frac"], reverse=True)
        # logging.info("%Slack ordering")
        # logging.info(ordered)
        bank = ordered[0]
        if bank["slack"] > 0:
            bank["width"] -= 1
            bank["slack"] -= 1
            bank["slack_frac"] = bank["slack"] / bank["ref"]["min"][1]
            total_slack -= 1
            diff += 1

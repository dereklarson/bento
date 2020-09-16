from bento import Bank
from bento import util as butil


class indicators(Bank):
    """

    Initialization Parameters
    -------------------------

    Attributes
    ----------

    Examples
    --------
    """

    # @logutil.loginfo(level='debug')
    def __init__(self, components, **kwargs):
        block_size = {"ideal": [2, 1.5], "min": [1, 1]}
        super().__init__(**kwargs)

        for ind_comp in components:
            name = ind_comp.get("name", ind_comp["args"]["y_column"])
            args = {
                "label": ind_comp.get("label", butil.titlize(name)),
                "H3.class": "h3",
            }
            indicator = self.create_component(
                "indicator", f"{name}_indicator", args=args
            )

            callback_code = f"""
                inputs = dictutil.strip_attr(inputs)
                filters = butil.prepare_filters(inputs)
                sig, scale = butil.aggregate(
                    sdf,
                    filters=filters,
                    **{ind_comp['args']}
                    )
                sig = f'{{float(f"{{sig:.3g}}"):g}}'
                return f"{{sig}} {{scale}}{ind_comp.get("unit", "")}"
                """

            cb_outputs = [(indicator.uid, "children")]
            self.add_callback(indicator.uid, cb_outputs, callback_code)

        self.align(block_size)

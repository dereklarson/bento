from bento import Bank
import bento.components as bc


class graph(Bank):
    """Displays any type of graph/chart/map. A cornerstone of most Bento apps.

    Initialization Parameters
    -------------------------
    category: string -- "normal" | "map"
        The category of graph to use. Most graphs are "normal", but any that include
        a geographical representation will be under the "map" category.
    variant: string
        Each category has a set of variants supported. The default category/variant
        is represented as "normal.scatter"
    kwargs: dict
        Passthrough of additional arguments that might get picked up at other levels
        such as the super() call.

    Attributes
    ----------

    Examples
    --------
    """

    def __init__(self, category="normal", variant="scatter", **kwargs):
        # NOTE Can be altered to provide a better sizing for the bank
        block_size = {"ideal": [8, 12], "min": [4, 4]}
        super().__init__(**kwargs)

        # Set dependent variable based on the type of graph
        if category == "map":
            dep_var = "z"
        else:
            dep_var = "y"

        cb_code = f"""
            inputs = dictutil.strip_attr(inputs)
            component_type = f"graph.{category}.{variant}"
            inputs = butil.apply_defaults(component_type, inputs, data)
            filters = butil.prepare_filters(inputs)
            transforms = butil.prepare_transforms(inputs, dep_var="{dep_var}")
            figure = Graph.{category}(sdf,
                variant="{variant}",
                filters=filters,
                transforms=transforms,
                **inputs)
            figure.update_layout(classes.graph)

            # This is used in conjunction with the loading overlay
            style={{'visibility': 'visible'}}

            return figure, style
            """

        # Generate the component calls
        id_dict = {"name": "graph", **self.uid}
        cid, component = bc.graph(id_dict, **kwargs)

        cb_outputs = [(cid, "figure"), (cid, "style")]
        self.add_callback(cid, cb_outputs, cb_code)

        blocks = [[[component]]]
        self.align(blocks, block_size)

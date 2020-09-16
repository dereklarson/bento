from bento import Bank


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
                filters=filters,
                transforms=transforms,
                **inputs)
            figure.update_layout(classes.graph)

            # This is used in conjunction with the loading overlay
            style={{'visibility': 'visible'}}

            return figure, style
            """

        # Generate the component calls
        graph = self.create_component("graph", name="graph", args={})
        cb_outputs = [(graph.uid, "figure"), (graph.uid, "style")]
        self.add_callback(graph.uid, cb_outputs, cb_code)
        self.align(block_size)

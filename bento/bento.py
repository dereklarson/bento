import black
import cerberus
import copy
import importlib
import pathlib
import re
from jinja2 import Environment, PackageLoader

from bento import util as butil
from bento import banks, grid, schema, style

from bento.common import logger, logutil, dictutil, codeutil  # noqa

logging = logger.fancy_logger(__name__, fmt="simple")


class Bento:
    def __init__(self, descriptor, init_only=False):
        """Converts the supplied descriptor into a jinja2 template context"""
        self.template = "bento_v1.py.j2"
        self.baseline_template = "baseline.css.j2"
        self.theme_template = "theme.css.j2"

        # Catches any problems with the input descriptor up front
        if not self.is_valid(descriptor):
            logging.warning("Exiting Bento intialization after failed validation")
            return

        # Stores a normalized version of the descriptor, ensuring uniformity
        self.desc = self.normalize(descriptor)

        # Loads the input data to inform components to the columns, types, etc
        self.data = self.process_data(self.desc)
        self.bb = banks.BentoBanks(self.data)

        # Generates the initial context object
        self.init_structure()

        if init_only:
            return

        logging.info("Creating the pages:")
        for pageid, page in self.desc["pages"].items():
            logging.info(f"#^  {pageid}...")
            self.create_page(pageid, page)
            # Specifies and attaches connectors to callbacks
            self.connect_page(page)
            logging.info(f"#$+ connected")

    # @logutil.loginfo(level='debug')
    def is_valid(self, descriptor):
        """Ensures a proper naming scheme is followed by the IDs"""
        logging.info("#^Testing validity of input descriptor...")
        validator = cerberus.Validator(schema.descriptor_schema)
        self.valid = validator.validate(descriptor)
        if not self.valid:
            logging.info("#$- failed")
            logging.warning("Descriptor validaiton failed due to the following errors:")
            logging.warning(validator.errors)
        else:
            logging.info("#$+ passed")

        return self.valid

    def bankid(self, pagename, bankname, delim="__"):
        return f"{pagename}{delim}{bankname}"

    # @logutil.loginfo(level='debug')
    def normalize(self, descriptor):
        """Auto-trims and -fills the descriptor
         - Removes any dangling bankids, assuming 'banks' keys as source of truth
         - Generates full bankid (pageid + bankname)
         - Handle most defaults here so they aren't scattered about
        """
        logging.info("#^Normalizing the input descriptor...")
        # TODO  Handle IDs here, perhaps with a utility class
        desc = copy.deepcopy(descriptor)

        desc["name"] = desc.get("name", "unspecified_name")
        desc["theme"] = desc.get("theme", "light")
        desc["data"] = desc.get("data", {})
        for data in desc["data"].values():
            # The default function call is assumed to be "load"
            if "call" not in data:
                data["call"] = "load"
            if "args" not in data:
                data["args"] = {}

        for pagename, page in desc["pages"].items():
            # Eliminate keys in connections that aren't in banks
            page["connections"] = dictutil.common_keys(
                page.get("connections", {}), page["banks"]
            )
            # Then rekey connections with both page and bank name
            page["connections"] = {
                self.bankid(pagename, from_bankname): {
                    self.bankid(pagename, to_bankname, delim="/")
                    for to_bankname in conn
                }
                for from_bankname, conn in page["connections"].items()
            }

            # Scan the layout for undefined banks and rekey
            new_layout = []
            for old_row in page.get("layout", []):
                new_row = []
                for bankname in old_row:
                    if bankname not in page["banks"]:
                        continue
                    new_item = {"bankid": self.bankid(pagename, bankname)}
                    new_row.append(new_item)
                new_layout.append(new_row)
            page["layout"] = new_layout

            # Scan the sidebar for undefined banks and rekey
            new_sidebar = []
            for bankname in page.get("sidebar", []):
                is_open = True
                if bankname.startswith("_"):
                    is_open = False
                    bankname = bankname.replace("_", "")
                if bankname not in page["banks"]:
                    continue
                new_item = {"bankid": self.bankid(pagename, bankname)}
                new_item["title"] = butil.titlize(bankname)
                new_item["open"] = is_open
                new_sidebar.append(new_item)
            page["sidebar"] = new_sidebar

            # Finally fix the banks
            new_banks = {}
            for bankname, bank in page["banks"].items():
                bank["args"] = bank.get("args", {})
                bank["args"]["gid"] = {"pageid": pagename, "bankid": bankname}
                new_banks[self.bankid(pagename, bankname)] = bank
            page["banks"] = new_banks
        logging.info("#$+ done")
        return desc

    def process_data(self, descriptor):
        logging.info("Loading the dataframes specified:")
        data = {}
        for dataid, entry in descriptor["data"].items():
            logging.info(f"  {dataid}:")
            try:
                data_module = importlib.import_module(entry["module"])
            except ImportError:
                logging.warning(f"Failed to load {entry['module']}")
                continue
            data[dataid] = getattr(data_module, entry["call"])(**entry["args"])
            data[dataid]["columns"] = list(data[dataid]["types"].keys())
            logging.info(f"    Loaded Dataframe of shape {data[dataid]['df'].shape}")
        return data

    def init_structure(self):
        logging.info("#^Generating initial context object...")
        # Outputs are a collection of fields provided by banks that are available
        # to be connected to other banks if the connections are provided
        # e.g. outputs + connections => connectors
        self.outputs = {}

        # Connectors define how the banks/components share information
        # They specify many-to-many <component_id>.<attribute> mappings
        # e.g. [axis_control.x_column, axis_control.y_column] -> graph.figure
        connectors = {
            "page": {
                "inputs": [("location", "pathname")],
                "outputs": [("page", "children")],
            }
        }

        # Callbacks are the boxes that the connectors connect. They take the inputs
        # and calculate the outputs, triggered when the inputs change.
        # TODO This needs generalization
        callback_code = """
            # Presumes only a simple url is passed in, probably enough for a template
            page_id = args[0].replace("/", "") if args[0] else "default"
            return page_index.get(page_id, list(page_index.values())[0])
            """

        callbacks = {
            "page": {"name": "update_page", "code": codeutil.format_code(callback_code)}
        }

        # This context contains the info fed into the Jinja template
        # The main job of the Bento class is to boil down the supplied description
        # into this context.
        self.theme_spec = style.BentoStyle(
            theme=self.desc.get("theme"), theme_dict=self.desc.get("theme_dict")
        ).spec
        self.context = {
            "name": self.desc["name"],
            "theme_spec": self.theme_spec,
            "appbar": self.desc.get("appbar", {}),
            "data": self.desc["data"],
            "pages": {},
            "banks": {},
            "connectors": connectors,
            "callbacks": callbacks,
        }
        logging.info("#$+ done")

    def create_page(self, pageid, page):
        # Prepares the definitions of the bank containers
        for bankid, bank in page["banks"].items():
            self.context["banks"][bankid] = self.build_bank(bank, page)

        self.outputs.update(self.bb.outputs)
        self.context["callbacks"].update(self.bb.callbacks)
        self.context["connectors"].update(self.bb.connectors)

        # Defines the layout of the page
        self.context["pages"][pageid] = grid.apply_grid(page)

    def connect_page(self, page):
        connections = page.get("connections", {})
        # Loop over all pairs of defined sources and sinks
        for source_bankid, sink_set in connections.items():
            for sink_regex in sink_set:
                for sink_cid, cb_def in self.context["callbacks"].items():
                    if not re.search(sink_regex, sink_cid):
                        continue
                    # Make sure we have a connector in place
                    if sink_cid not in self.context["connectors"]:
                        # The callback defines what component properties it provides
                        sink_vals = cb_def["provides"]
                        self.context["connectors"][sink_cid] = {
                            "outputs": [(sink_cid, val) for val in sink_vals],
                            "inputs": set(),
                        }
                    # Add any connected inputs
                    # TODO The bankid.replace needs to be improved
                    for cid, var in dictutil.extract(
                        source_bankid.replace("__", "/"), self.outputs, pop=False
                    ).items():
                        self.context["connectors"][sink_cid]["inputs"].add((cid, var))

    # @logutil.loginfo(level='debug')
    def build_bank(self, bank, page):
        # TODO Think through defaults on data, or perhaps just require a dataid
        args = {"dataid": "default"}
        # Get any page-level arguments
        args.update(dictutil.extract("dataid", page, pop=False))
        # Overwrite with specific args for bank
        args.update(bank["args"])
        item, sizing = getattr(self.bb, bank["type"])(**args)
        if "width" in bank:
            sizing["min"][1] = bank["width"]
            sizing["ideal"][1] = bank["width"]
        bank["sizing"] = sizing
        return item

    def write(self, app_output="bento_app.py", css_folder="assets"):
        if not self.valid:
            logging.warning("Descriptor never validated")
            return
        logging.info("Writing Dash application files:")
        self.write_template(self.context, self.template, app_output)

        pathlib.Path(css_folder).mkdir(parents=True, exist_ok=True)
        spec = style.BentoStyle(theme_dict=self.theme_spec).spec

        out_file = self.baseline_template.replace(".j2", "")
        self.write_template(spec, self.baseline_template, f"{css_folder}/{out_file}")

        out_file = self.theme_template.replace(".j2", "")
        self.write_template(spec, self.theme_template, f"{css_folder}/{out_file}")

    def write_template(self, context, template, output_location):
        env_args = {"trim_blocks": True, "lstrip_blocks": True}
        jenv = Environment(loader=PackageLoader(__name__), **env_args)
        template = jenv.get_template(template)
        str_output = template.render(context)

        # TODO Probably harden this against leaks
        if ".py" in output_location:
            mode = black.FileMode()
            try:
                str_output = black.format_file_contents(
                    str_output, fast=True, mode=mode
                )
            except Exception:
                logging.warning("Issue using Black to format file output")

        with open(output_location, "w") as fh:
            fh.write(str_output)

        logging.info(f"  wrote {output_location}")

import black
import copy
import importlib
import re
from jinja2 import Environment, PackageLoader

from bento import util as butil
from bento.banks import BentoBanks
from bento import grid

from bento.common import logger, logutil, dictutil, codeutil  # noqa

# from bento.common.structure import ENV

logging = logger.fancy_logger(__name__, fmt="simple")


class Bento:
    # @logutil.logdebug
    def __init__(self, descriptor):
        # TODO Use theme template with self.init_theme()
        # self.template = "dash_grid_theme.py"
        self.template = "dash_grid_comps.py"

        logging.info("Testing validity of input descriptor...")
        if not self.is_valid(descriptor):
            return
        logging.info("Normalizing the input descriptor...")
        self.desc = self.normalize(descriptor)
        self.name = self.desc.get("name", "unspecified_name")
        self.theme = self.desc.get("theme", "light")

        logging.info("Loading the dataframes specified...")
        self.data = self.process_data(self.desc)
        self.bb = BentoBanks(self.data)

        logging.info("Generating initial context object...")
        self.init_structure()
        # TODO Currently disabled, until we can figure out how to get it to work well
        # self.init_theme()

        logging.info("Creating the pages...")
        page_dict = self.desc["pages"]
        for pageid, page in page_dict.items():
            logging.info(f"    {pageid}")
            self.create_page(pageid, page)
            # Specifies and attaches connectors to callbacks
            logging.info(f"    ...connecting...")
            self.connect_page(page)

    def is_valid(self, descriptor):
        """Ensures a proper naming scheme is followed by the IDs"""
        # A string of word characters only with length 2+
        id_regex = re.compile(r"^\w{2,}$")
        valid_flag = True
        for pageid, page in descriptor.get("pages", {}).items():
            if not id_regex.match(pageid):
                logging.warning(f"Page ID '{pageid}' isn't a valid name")
                valid_flag = False
            for bankid, bank in page.get("banks", {}).items():
                if not id_regex.match(bankid):
                    logging.warning(f"Bank ID '{bankid}' isn't a valid name")
                    valid_flag = False

        # Check for a single-page dash
        for bankid, bank in descriptor.get("banks", {}).items():
            if not id_regex.match(bankid):
                logging.warning(f"Bank ID '{bankid}' isn't a valid name")
                valid_flag = False

        return valid_flag

    def bankid(self, pagename, bankname, delim="_"):
        return f"{pagename}{delim}{bankname}"

    # @logutil.logdebug
    def normalize(self, descriptor):
        """Auto-trims and -fills the descriptor
         - Removes any dangling bankids, assuming 'banks' key as source of truth
         - Generates full bankid (pageid + bankname)
        """
        # TODO  Handle IDs here, perhaps with a utility class
        desc = copy.deepcopy(descriptor)
        if "pages" not in desc:
            desc["pages"] = {
                "main": {
                    "dataid": desc["dataid"],
                    "banks": desc["banks"],
                    "layout": desc.get("layout", []),
                    "sidebar": desc.get("sidebar", []),
                    "connections": desc["connections"],
                }
            }

        for data in desc.get("data", {}).values():
            if "call" not in data:
                data["call"] = "load"
            if "args" not in data:
                data["args"] = {}

        for pagename, page in desc.get("pages", {}).items():
            # Eliminate keys in connections that aren't in banks
            page["connections"] = dictutil.common_keys(
                page["connections"], page["banks"]
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
                if bankname not in page["banks"]:
                    continue
                new_item = {"bankid": self.bankid(pagename, bankname)}
                new_item["title"] = butil.titlize(bankname)
                new_sidebar.append(new_item)
            page["sidebar"] = new_sidebar

            # Finally fix the banks
            new_banks = {}
            for bankname, bank in page["banks"].items():
                if "args" not in bank:
                    bank["args"] = {}
                bank["args"]["gid"] = {"pageid": pagename, "bankid": bankname}
                new_banks[self.bankid(pagename, bankname)] = bank
            page["banks"] = new_banks
        return desc

    def process_data(self, descriptor):
        data = {}
        for dataid, entry in descriptor["data"].items():
            try:
                data_module = importlib.import_module(entry["module"])
            except ImportError:
                logging.warning(f"Failed to load {entry['module']}")
                continue
            data[dataid] = getattr(data_module, entry["call"])(**entry["args"])
            data[dataid]["columns"] = list(data[dataid]["types"].keys())
        return data

    def init_structure(self):
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
        self.context = {
            "name": self.name,
            "theme": self.desc.get("theme", "light"),
            "main": self.desc.get("main", {}),
            "data": self.desc["data"],
            "pages": {},
            "banks": {},
            "connectors": connectors,
            "callbacks": callbacks,
        }

    def init_theme(self):
        # TODO Currently disabled, until we can figure out how to get it to work well

        page_out = ["({'page': dd.ALL}, 'style')", "({'page': dd.ALL}, 'className')"]
        self.context["connectors"]["theme"] = {
            "inputs": [("location", "pathname")],
            "outputs": [("main", "style"), ("app_bar", "style")] + page_out,
        }

        callback_code = """
            # Presumes only a simple url is passed in, probably enough for a template
            page_id = args[0].replace("/", "") if args[0] else "default"
            themes = {'mars': 'light', 'stock': 'dark flat sparse'}
            _classes = BentoStyle(theme=themes.get(page_id, ""))
            output = [_classes.main, _classes.app_bar]
            # output.extend([_classes.grid, _classes.theme["class_name"]])
            return output
            """

        self.context["callbacks"]["theme"] = {
            "name": "update_theme",
            "code": codeutil.format_code(callback_code),
        }

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
                        source_bankid.replace("_", "/"), self.outputs, pop=False
                    ).items():
                        self.context["connectors"][sink_cid]["inputs"].add((cid, var))

    # @logutil.logdebug
    def build_bank(self, bank, page):
        # Get any page-level arguments
        args = dictutil.extract("dataid", page, pop=False)
        # Overwrite with specific args for bank
        args.update(bank["args"])
        item, sizing = getattr(self.bb, bank["type"])(**args)
        if "width" in bank:
            sizing["min"][1] = bank["width"]
            sizing["ideal"][1] = bank["width"]
        bank["sizing"] = sizing
        return item

    def write(self, filename="generated_template.py"):
        # TODO Finish
        env_args = {"trim_blocks": True, "lstrip_blocks": True}
        jenv = Environment(loader=PackageLoader(__name__), **env_args)
        template = jenv.get_template(self.template)

        with open(filename, "w") as fh:
            mode = black.FileMode()
            str_output = template.render(self.context)
            try:
                fh.write(black.format_file_contents(str_output, fast=True, mode=mode))
            except Exception:
                fh.write(str_output)

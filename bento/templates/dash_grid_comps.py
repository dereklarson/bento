import datetime
import numpy
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from bento.style import BentoStyle
from bento.graph import Graph
import bento.util as butil

# TODO merge the few dictutil items into bento util in bento repo
from bento.common import logger, dictutil

# Import the supplied data loading modules
{% for dataid, entry in data.items() %}
import {{entry['module']}} as {{dataid}}_data
{% endfor %}

logging = logger.fancy_logger(__name__)

logging.info("Creating the Dash application...")
app = dash.Dash("{{name}}")

# Need to suppress this for multi-page apps
app.config.suppress_callback_exceptions = True

# This should contain any non-interactive data prep required
logging.info("Loading the application data frames...")
data = {
    {% for dataid, entry in data.items() %}
    "{{dataid}}": {{dataid}}_data.{{entry['call']}}(**{{entry['args']}}),
    {% endfor %}
    }

# Supported themes: light, dark, ...
classes = BentoStyle(theme="{{theme}}", theme_dict={{theme_dict}})

# --- Layout ---
# Top-level: A main div containing two children: appbar and page content
main_children = [
  dcc.Location(id="location", refresh=False),
  html.Div(
    [
      html.Div([
        html.H1("{{appbar.title}}", id='title', style=classes.h1),
      {% if appbar.subtitle %}
        html.H3("{{appbar.subtitle}}", id='subtitle', style=classes.h3),
      {% endif %}
      ], style=classes.titles),
      {% if pages|length > 1 %}
        html.Div([
        {% for uid in pages %}
          dcc.Link(
              html.Button("{{uid}}", style=classes.button),
              href="/{{uid}}",
              style=classes.link),
        {% endfor %}
          ], style=classes.link_set),
      {% endif %}
      ], style=classes.appbar),
  html.Div(id="page", style=classes.page),
  ]
app.layout = html.Div(children=main_children, id="main", style=classes.main)

# Define the banks that comprise the pages (assembled into a grid later)
# Each bank is a 2-d list of dash components
{% for bank_id, bank in banks.items() %}
{{bank_id}} = [
  {% for bar in bank %}
  html.Div([
    {% for component in bar %}
    html.Div([
      {% if component.label %}
      html.Label("{{component.label}}", style=classes.label),
      {% endif %}
      dcc.Loading(
          {{component.lib}}.{{component.component}}(**{{component.args}}),
          type="default",
          ),
    ], 
    style={**classes.{{component.lib}}, **classes.block}),
    {% endfor %}
  ], style=classes.bar, className=classes.theme['class_name']),
  {% endfor %}
]

{% endfor %}

# Each page definition is a grid of bootstrap Rows and Cols containing Banks
{% for page_id, page in pages.items() %}
{{page_id}}_page = html.Div(id='{{page_id}}', children=[
  {% if page.intro %}
  # TODO Insert a new page explanation section (not using dbc.Modal)
  {% endif %}
    {% if page.sidebar %}
    html.Div([
      {% for bank in page.sidebar %}
      html.Details([
        html.Summary("{{bank.title}}"),
        *{{bank.bankid}},
        ], open=True),
      {% endfor %}
      ], style={"gridColumn": "1 / 3", **classes.paper}),
    {% endif %}
    {% for bank in page.banks %}
    html.Div({{bank.bankid}}, style={
             "gridColumn": "{{bank.column}} / span {{bank.width}}", **classes.paper}),
    {% endfor%}
],
  style=classes.grid)
{% endfor %}

# Bundle the pages together for use in the Location callback
page_index = {
{% for uid, page in pages.items() %}
  "{{uid}}": {{uid}}_page,
{% endfor %}
}

# Stores info like the titles to use for each page
page_context = {
{% for uid, page in pages.items() %}
  "{{uid}}": {
      "title": "{{page.title}}",
      "subtitle": "{{page.subtitle}}",
      },
{% endfor %}
}

# --- Callbacks ---
@app.callback(
        [Output("title", "children"), Output("subtitle", "children")],
        [Input("location", "pathname")])
def update_title(*args):
    # Presumes only a simple url is passed in, probably enough for a template
    page_id = args[0].replace("/", "") if args[0] else "default"
    title = page_context.get(page_id, {}).get("title") or "{{appbar.title}}"
    subtitle = page_context.get(page_id, {}).get("subtitle") or "{{appbar.subtitle}}"
    return title, subtitle

{% for uid, conn in connectors.items() %}
@app.callback(
  {% if conn.outputs|length == 1 %}
    Output{{conn.outputs[0]}}, [
  {% else %}
  [
    {% for out in conn.outputs|sort %}
    Output{{out}},
    {% endfor %}
  ], [
  {% endif %}
  {% for inp in conn.inputs|sort %}
    Input{{inp}},
  {% endfor %}
  ])
def {{callbacks[uid].name}}(*args):
{{callbacks[uid].code}}
{% endfor %}

if __name__ == '__main__':
    app.run_server(debug=False)


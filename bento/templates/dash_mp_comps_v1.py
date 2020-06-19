import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from bento.style import BentoStyle
from bento.graph import Graph
import bento.util as butil

# TODO merge the few dictutil items into bento util in bento repo
from common import logger, dictutil

# Import the supplied data loading modules
{% for dataid, entry in data.items() %}
import {{entry['module']}} as {{dataid}}_data
{% endfor %}

logging = logger.fancy_logger(__name__)

# app = dash.Dash("{{name}}")
# The dbc GRID theme provides the column sizes, etc for the grid system
app = dash.Dash("{{name}}", external_stylesheets=[dbc.themes.GRID])
# NOTE modal classes come from the Bootstrap theme for now, until we separate them
# app = dash.Dash("{{name}}", external_stylesheets=[dbc.themes.BOOTSTRAP])


# Need to suppress this for multi-page apps
app.config.suppress_callback_exceptions = True

# This should contain any non-interactive data prep required
data = {
    {% for dataid, entry in data.items() %}
    "{{dataid}}": {{dataid}}_data.{{entry['call']}}(**{{entry['args']}}),
    {% endfor %}
    }

# Supported themes: light, dark, ...
classes = BentoStyle(theme="{{theme}}", mode="{{mode}}", debug=False)

# --- Layout ---
# Top-level: A main div containing the title and page links
main_children = [
  dcc.Location(id="location", refresh=False),
  html.Div(
    [
      html.Div([
        html.H1("{{main.title}}", style=classes.h1),
      {% if main.subtitle %}
        html.H3("{{main.subtitle}}", style=classes.h3),
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
      ], style=classes.app_bar),
  html.Div(id="page", style=classes.page),
  ]
app.layout = html.Div(children=main_children, id="main", style=classes.main)

# Define the banks that comprise the pages (assembled into a grid later)
# Each bank is a 2-d list of dash components
{% for bank_id, bank in banks.items() %}
{{bank_id}} = html.Div([
  {% for bar in bank %}
  html.Div([
    {% for component in bar %}
    html.Div([
      {% if component.label %}
      html.Label("{{component.label}}", style=classes.label),
      {% endif %}
      {{component.lib}}.{{component.component}}(**{{component.args}}),
    ], style={**classes.{{component.lib}}, **classes.block}),
    {% endfor %}
  ], style=classes.bar, className=classes.theme['class_name']),
  {% endfor %}
], style=classes.paper)

{% endfor %}

# Each page definition is a grid of bootstrap Rows and Cols containing Banks
{% for page_id, page in pages.items() %}
{{page_id}}_page = html.Div(id='{{page_id}}', children=[
  {% if page.intro %}
  dbc.Modal(
    [
      dbc.ModalHeader("Introduction to {{page_id}}", style=classes.modal_header),
      dbc.ModalBody("{{page.intro}}", style=classes.modal_body),
      dbc.ModalFooter("Click elsewhere to close", style=classes.modal_footer),
    ],
    id="modal-centered",
    is_open=True,
    centered=True,
    style=classes.modal
  ),
  {% endif %}
  dbc.Row(children=[
    {% if page.sidebar %}
    dbc.Col([
      {% for bank in page.sidebar %}
      html.Details([
        html.Summary("{{bank.bankid}}"),
        {{bank.bankid}},
        ], open=True),
      {% endfor %}
        ], width=2, style=classes.col),
    {% endif %}
    dbc.Col([
      {% for row in page.layout %}
      dbc.Row([
      {% for col in row %}
        dbc.Col([{{col.bankid}}],
          {% if col.width %}
          width={{col.width}},
          {% endif %}
          style=classes.col),
        {% endfor %}
        ], style=classes.row),
      {% endfor %}
      ], width={{page.width}}, style=classes.col)
    ], style={"height": "100vh", **classes.row})
])
{% endfor %}

# Bundle the pages together for use in the Location callback
page_index = {
{% for uid, page in pages.items() %}
  "{{uid}}": {{uid}}_page,
{% endfor %}
}

# --- Callbacks ---
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
    app.run_server(debug=True)


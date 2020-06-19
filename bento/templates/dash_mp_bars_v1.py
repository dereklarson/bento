import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from bento.style import BentoStyle
from bento.graph import Graph
import bento.util as butil

from common import logger, dictutil
from loaddata import example

logging = logger.fancy_logger(__name__)

app = dash.Dash("{{name}}", external_stylesheets=[dbc.themes.GRID])

# Need to suppress this for multi-page apps
app.config.suppress_callback_exceptions = True

# NOTE Try to keep the configurable content here
data = example.load('./')

# Supported themes: light, dark, ...
classes = BentoStyle(theme="{{theme}}", debug=False)

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
      ],
      style=classes.app_bar,
    ),
  html.Div(id="content", style=classes.content),
  ]
app.layout = html.Div(children=main_children, id="main", style=classes.main)

# Define the banks that comprise the pages (assembled into a grid later)
# Each bank is a 2-d list of dash components
{% for bank_id, bank in banks.items() %}
{{bank_id}} = html.Div([
  {% for bar in bank %}
  butil.Bar([
    {% for component in bar %}
    {{component}},
    {% endfor %}
  ], style_ref=classes.styles_in_bar, className=classes.theme['class_name']),
  {% endfor %}
], style=classes.paper)
{% endfor %}

# Each page definition is a grid of bootstrap Rows and Cols containing Banks
{% for page_id, page in pages.items() %}
{{page_id}}_page = html.Div(id='{{page_id}}', children=[
  {% for row in page %}
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
])
{% endfor %}

# Bundle the pages into the content dictionary
content = {
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
{{callbacks[uid]}}
{% endfor %}

if __name__ == '__main__':
    app.run_server(debug=True)


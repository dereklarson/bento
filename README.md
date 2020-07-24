# Bento

[![GitHub](https://img.shields.io/github/license/dereklarson/bento?style=for-the-badge)](https://github.com/dereklarson/bento/blob/master/LICENSE)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/dereklarson/bento?style=for-the-badge)](https://github.com/dereklarson/bento/graphs/contributors)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/dereklarson/bento.svg?style=for-the-badge)](https://lgtm.com/projects/g/dereklarson/bento/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/dereklarson/bento.svg?style=for-the-badge)](https://lgtm.com/projects/g/dereklarson/bento/alerts/)

Create Plotly Dash apps via a template

## Quickstart
Dependencies: Python 3.7+

Bento is currently on the test PyPI repository, and can be installed with:

`pip3 install --index-url https://test.pypi.org/simple/ bento-dash==0.1.6`

To make sure everything is working, try building the demo app:

`python3 -m bento.dashboards.demo`

If there are no warnings, you should see `bento_app.py` and `assets/`.
You can now run:

`python3 bento_app.py`

And navigate in your browser to `localhost:8050`.

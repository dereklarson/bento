# Bento

[![GitHub](https://img.shields.io/github/license/dereklarson/bento?style=for-the-badge)](https://github.com/dereklarson/bento/blob/master/LICENSE)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/dereklarson/bento?style=for-the-badge)](https://github.com/dereklarson/bento/graphs/contributors)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/dereklarson/bento.svg?style=for-the-badge)](https://lgtm.com/projects/g/dereklarson/bento/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/dereklarson/bento.svg?style=for-the-badge)](https://lgtm.com/projects/g/dereklarson/bento/alerts/)

### *Create Plotly Dash apps via templates*

![Bento Example](bento_example.gif)

Bento is a templating engine built on [Plotly Dash](https://plotly.com/dash/). It lets you
write a high-level description of your desired interactive dashboard and generates
the application code for you. By providing a set of reusable building blocks and
abstracting away some of the more complicated aspects, it aims to flatten the learning
curve of dashboarding!

## Quickstart
Dependencies: Python 3.7+

Bento is available on PyPI, and the latest version can be installed with:

`pip3 install bento-dash`

To make sure everything is working, try running the demo app:

`bento-demo`

And navigate in your browser to `localhost:8050`.

## Developing with Bento
If you're interested in creating and deploying a Bento dashboard, I recommend setting
up a Docker-friendly environment. I created a repo that can get you going called
[Bento Builder](https://github.com/dereklarson/bento_builder).

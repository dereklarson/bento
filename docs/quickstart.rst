Quickstart
==========
To get started with Bento, we're going to walk through a few quick steps:

- Installation
- Run the demo dashboard 
- Modify the demo
- Fall back to straight Plotly Dash
- Clone Bento Builder

Installation
------------
Dependencies: Python 3.7+

Bento is available on PyPI, and the latest version can be installed with::

$ pip3 install bento-dash

Run Demo
--------
To make sure everything is working, try running the demo app::

$ bento-demo

And navigate in your browser to `localhost:8050`.

Modify Demo
-----------
To get a quick taste of the Bento experience, now run the following::

$ python3 -m bento.dashboards.demo
$ python3 -m bento.launcher

The first will write out a copy of the demo descriptor to your current dir.
You can then open that up and modify it while the server from the second
command is up.

It'll be hard to know what to change, so here's a few quick things to try:
 * Comment out the ``"theme": "dark"`` line (Refresh your browser so the CSS updates!)
 * Comment out and of the pages from the descriptor top-level
 * Reorder the layouts
 * Comment out any bank
 * Disconnect a bank by removing it from the ``connections``

Fallback
--------
At any point, if you've started an app with Bento but can't figure out how to
go further, you can always continue by editing the base app code. After either
of the last steps, you will have a ``bento_app.py`` file plus associated files
in ``assets/`` (check the log output while running Bento). These can be edited,
and then you can run the changes with::

$ python3 bento_app.py

.. note::
    Bento does make use of several utility functions included in the bento Python
    package. To fully be independent, you'd need to copy those over as well.

Bento Builder
-------------
If you've jumped through the above hoops and are looking for a way to develop
efficiently, I recommend cloning/templating from the `Bento Builder
<https://github.com/dereklarson/bento_builder>`_ repo! Some quickstart steps
are available in the readme.

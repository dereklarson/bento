API Reference
=============

.. contents::
    :local:
    :depth: 1

Bento class
-----------
.. automodule:: bento.bento
.. autoclass:: Bento
   :members:

Descriptor schema
-----------------
To get a quick sense of the schema, I recommend looking at the following examples:
 - `A bare-bones dash <https://github.com/dereklarson/bento/blob/master/bento/dashboards/simple.py>`_
   - Run ``python3 -m bento.dashboards.simple`` then ``python3 bento_app.py`` to view 
 - `The demo dash <https://github.com/dereklarson/bento/blob/master/bento/dashboards/demo.py>`_
   - Run ``bento-demo`` to see it in action

The full schema follows, which, for now, is a simple dump of the Cerberus schema:

.. literalinclude:: ../bento/schema.py
   :language: python
   :lines: 1-

Utility functions
-----------------
.. raw:: html

   <details>
   <summary><a>Test folding</a></summary>

.. autofunction:: bento.util.desnake

.. raw:: html

   </details>

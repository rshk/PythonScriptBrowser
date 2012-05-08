PythonScript Browser
####################

This project goal is to create a webkit-based web browser that is able
to run Python scripts just as it would with JavaScript.

This is accomplished right now by extracting all the
``<script type="text/python">`` from the web page and executing them in a
modified environment (eg. passing objects such as ``document``, some
utility functions, etc.).

At the moment it should be used only for trusted applications, as the Python
code have full access to everything; a future goal is to create a protection
layer that would allow applications to do certain things only upon user's
approval.

All the event handling part is quite hackerish, as the ``QtWebKit`` objects
don't provide a way to properly connect/handle DOM events.

Instead, we are using a bit of javascript that simulates the click on an
``event://...`` link that is then intercepted and passed to the appropriate
listener.

Installation
============

The only requirements right now are PyQt4 and demjson::

    apt-get install python-qt4
    pip install demjson

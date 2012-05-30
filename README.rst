PythonScript Browser
####################

Project goal
============

This project goal is to create a webkit-based web browser that is able
to run Python scripts just as it would with JavaScript.

This is accomplished right now by extracting all the
``<script type="application/x-python">`` from the web page and executing
them in a modified environment (eg. passing objects such as ``document``,
some utility functions, a custom ``__import__``, etc.).

The whole thing is very much hackerish in many ways, eg:

 * We are using a custom ``__builtin__`` module that overrides
   ``__import__`` in order to allow (in future) importing modules
   from http; but using custom ``__builtins__`` makes Python run in
   "restricted mode", disallowing some actions such as creating
   ``file`` objects; in order to prevent these limitations, we are
   using a custom ``open()`` too..
 * There's no straight-forward way in ``QtWebKit`` to catch DOM events;
   instead, we are using some javascript that simulates a click on an
   ``event://`` link, containing event information in the URL; this way we
   can catch it (a signal is emitted when links are clicked) and
   call the appropriate handler.
 * Simple redirections are **not** catchable by ``QtWebKit``, so, instead
   of using something like ``location.href = "..."`` for the above, we
   have to create a DOM ``a`` element and simulate a ``mouseclick`` event
   on it..
 * Along with ``event://``, there's a similar way to implement (quicker)
   ``action://``, using something like::

        window.onAction('my-action', my_action_handler)
        def my_action_handler():
            ## Do something
            pass

   And in the HTML::

        <a href="action://my-action">My Action</a>


.. warning::
	At the moment it should be used only for trusted applications, as the Python
	code have full access to everything; a future goal is to create a protection
	layer that would allow applications to do certain things only upon user's
	approval.

.. note::
	The only safe way to add a security layer seems to be using PyPy's
	sandbox that wraps C functions calls; the ``rexec`` module is considered
	insecure and should not be used.

Installation
============

The only requirements right now are PyQt4 and demjson::

    apt-get install python-qt4
    pip install demjson

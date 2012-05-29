"""Custom builtins module for the PythonScript interpreter"""


import __builtin__
import imp

## We want the real __import__
python_import = __import__

def custom_import(name, globals={}, locals={}, fromlist=[], level=-1):
    """Custom Import function can be used to import stuff from non-standard
    locations, eg. modules from the application directory.

    We don't add that directory to the path, as it might be on an http
    location, and as such we have to try loading the module from http.

    .. warning::
        Custom import function cannot be used to prevent the application
        to import "dangerous" modules. The only way to secure that, is by
        using something like pypy's sandbox.
    """

    ## Does nothing at the moment

    print "++++ IMPORT : %r - %r ++++" % (name, fromlist)
    return python_import(name, globals, locals, fromlist, level)

def custom_open(name, *a, **kw):
    """Escape from restricted environment created due to use
    of custom __builtin__"""
    print "+++ OPEN: %r" % name
    return __builtin__.open(name, *a, **kw)


def create_builtins():
    """Create custom __builtin__ module"""
    builtins = imp.new_module('__builtin__')
    builtins.__dict__.update(__builtin__.__dict__)
    builtins.__import__ = custom_import
    builtins.open = custom_open
    return builtins

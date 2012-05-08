"""Custom builtins module for the PythonScript interpreter
"""
import __builtin__
import imp

class PermissionDenied(Exception): pass

def _disabled(*a, **kw):
    raise PermissionDenied, "Calling this function was denied by the user"

def custom_import(name, globals={}, locals={}, fromlist=[], level=-1):
    """Custom Import function that denies importing of some unsafe modules
    """
    ## List of dangerous modules that can NEVER be imported
    disabled_modules = ['__builtin__', 'imp']
    use_safe_version = ['os', 'posixpath']
    modules_requiring_permissions = ['string', 'json']
    modules_permissions_allowed = []

    if name in disabled_modules:
        raise PermissionDenied, "Importing module %r is disabled" % name
    elif name in use_safe_version:
#        >>> f0 = imp.find_module('browsersafe')
#        >>> l0 = imp.load_module('browsersafe', *f0)
#        >>> f1 = imp.find_module('os', [l0.__path__])
#        Traceback (most recent call last):
#        File "<stdin>", line 1, in <module>
#        ImportError: No module named os
#        >>> f1 = imp.find_module('os', path=l0.__path__)
#        Traceback (most recent call last):
#        File "<stdin>", line 1, in <module>
#        TypeError: find_module() takes no keyword arguments
#        >>> f1 = imp.find_module('os', l0.__path__)
#        >>> l1 = imp.load_module('os', *f1)
#        >>> l1
#        <module 'os' from 'browsersafe/os.pyc'>
        browsersafe_found = imp.find_module('browsersafe')
        browsersafe = imp.load_module('browsersafe', *browsersafe_found)
        mparts = name.split('.')
        _searchpath = browsersafe.__path__
        for i, p in enumerate(mparts):
            found_module = imp.find_module(p, _searchpath)
            loaded_module = imp.load_module('.'.join(mparts[:i+1]), *found_module)
            try:
                _searchpath = loaded_module.__path__
            except AttributeError:
                return loaded_module
        #return loaded_module


        #return __builtin__.__import__("browsersafe.%s" % name, globals, locals, fromlist, level)

    elif name in modules_requiring_permissions:
        if name not in modules_permissions_allowed:
            from PyQt4.QtGui import QMessageBox
            answer = QMessageBox.question(None,
                "Application is asking permissions",
                "The application is wanting to use the module %s. Do you want to allow it to do so?" % name,
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Cancel)
            if answer != QMessageBox.Ok:
                raise PermissionDenied, "The used denied permission to import module %s" % name

    #print "++++ IMPORT : %r - %r ++++" % (name, fromlist)
    return __builtin__.__import__(name, globals, locals, fromlist, level)

import os
def _issubpath(a, b):
    def fixpath(p):
        return os.path.normpath(os.path.abspath(p)) + os.sep
    return fixpath(a).startswith(fixpath(b))

def open(name, *a, **kw):
    allowed_paths = [
        '/tmp/pythonscript-browser-storage',
        ## TODO: Do this in a better way - relative to application?
        os.path.abspath(os.path.join(os.path.dirname(__file__), 'pages')),
        os.path.abspath(os.path.join(os.path.dirname(__file__), 'misc')),
        ]
    #if not _issubpath()
    if not any([_issubpath(name, p) for p in allowed_paths]):
        raise PermissionDenied, "The file path is outside the allowed paths"
    print "+++ OPEN: %r" % os.path.normpath(os.path.abspath(name))
    return __builtin__.open(name, *a, **kw)


## Exceptions
ArithmeticError = __builtin__.ArithmeticError
AssertionError = __builtin__.AssertionError
AttributeError = __builtin__.AttributeError
BaseException = __builtin__.BaseException
BufferError = __builtin__.BufferError
BytesWarning = __builtin__.BytesWarning
DeprecationWarning = __builtin__.DeprecationWarning
EOFError = __builtin__.EOFError
Ellipsis = __builtin__.Ellipsis
EnvironmentError = __builtin__.EnvironmentError
Exception = __builtin__.Exception
FloatingPointError = __builtin__.FloatingPointError
FutureWarning = __builtin__.FutureWarning
GeneratorExit = __builtin__.GeneratorExit
IOError = __builtin__.IOError
ImportError = __builtin__.ImportError
ImportWarning = __builtin__.ImportWarning
IndentationError = __builtin__.IndentationError
IndexError = __builtin__.IndexError
KeyError = __builtin__.KeyError
KeyboardInterrupt = __builtin__.KeyboardInterrupt
LookupError = __builtin__.LookupError
MemoryError = __builtin__.MemoryError
NameError = __builtin__.NameError
NotImplemented = __builtin__.NotImplemented
NotImplementedError = __builtin__.NotImplementedError
OSError = __builtin__.OSError
OverflowError = __builtin__.OverflowError
PendingDeprecationWarning = __builtin__.PendingDeprecationWarning
ReferenceError = __builtin__.ReferenceError
RuntimeError = __builtin__.RuntimeError
RuntimeWarning = __builtin__.RuntimeWarning
StandardError = __builtin__.StandardError
StopIteration = __builtin__.StopIteration
SyntaxError = __builtin__.SyntaxError
SyntaxWarning = __builtin__.SyntaxWarning
SystemError = __builtin__.SystemError
SystemExit = __builtin__.SystemExit
TabError = __builtin__.TabError
TypeError = __builtin__.TypeError
UnboundLocalError = __builtin__.UnboundLocalError
UnicodeDecodeError = __builtin__.UnicodeDecodeError
UnicodeEncodeError = __builtin__.UnicodeEncodeError
UnicodeError = __builtin__.UnicodeError
UnicodeTranslateError = __builtin__.UnicodeTranslateError
UnicodeWarning = __builtin__.UnicodeWarning
UserWarning = __builtin__.UserWarning
ValueError = __builtin__.ValueError
Warning = __builtin__.Warning
ZeroDivisionError = __builtin__.ZeroDivisionError
#_ = __builtin__._
#__debug__ = __builtin__.__debug__
#__doc__ = __builtin__.__doc__
#__import__ = __builtin__.__import__
#__name__ = __builtin__.__name__
#__package__ = __builtin__.__package__

## Builtin functions
abs = __builtin__.abs
all = __builtin__.all
any = __builtin__.any
apply = __builtin__.apply
basestring = __builtin__.basestring
bin = __builtin__.bin
bool = __builtin__.bool
buffer = __builtin__.buffer
bytearray = __builtin__.bytearray
bytes = __builtin__.bytes
callable = __builtin__.callable
chr = __builtin__.chr
classmethod = __builtin__.classmethod
cmp = __builtin__.cmp
coerce = __builtin__.coerce
compile = _disabled
complex = __builtin__.complex
copyright = __builtin__.copyright
credits = __builtin__.credits
delattr = __builtin__.delattr
dict = __builtin__.dict
dir = __builtin__.dir
divmod = __builtin__.divmod
enumerate = __builtin__.enumerate
eval = _disabled
execfile = _disabled
exit = __builtin__.exit
file = _disabled
filter = __builtin__.filter
float = __builtin__.float
format = __builtin__.format
frozenset = __builtin__.frozenset
getattr = __builtin__.getattr
globals = __builtin__.globals
hasattr = __builtin__.hasattr
hash = __builtin__.hash
help = __builtin__.help
hex = __builtin__.hex
id = __builtin__.id
input = __builtin__.input
int = __builtin__.int
intern = __builtin__.intern
isinstance = __builtin__.isinstance
issubclass = __builtin__.issubclass
iter = __builtin__.iter
len = __builtin__.len
license = __builtin__.license
list = __builtin__.list
locals = __builtin__.locals
long = __builtin__.long
map = __builtin__.map
max = __builtin__.max
min = __builtin__.min
next = __builtin__.next
object = __builtin__.object
oct = __builtin__.oct
#open = _disabled
ord = __builtin__.ord
pow = __builtin__.pow
#print = __builtin__.print
property = __builtin__.property
quit = __builtin__.quit
range = __builtin__.range
raw_input = __builtin__.raw_input
reduce = __builtin__.reduce
reload = __builtin__.reload
repr = __builtin__.repr
reversed = __builtin__.reversed
round = __builtin__.round
set = __builtin__.set
setattr = __builtin__.setattr
slice = __builtin__.slice
sorted = __builtin__.sorted
staticmethod = __builtin__.staticmethod
str = __builtin__.str
sum = __builtin__.sum
super = __builtin__.super
tuple = __builtin__.tuple
type = __builtin__.type
unichr = __builtin__.unichr
unicode = __builtin__.unicode
vars = __builtin__.vars
xrange = __builtin__.xrange
zip = __builtin__.zip

## Here since we need the real __import__ in this module..
__import__ = custom_import

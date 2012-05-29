#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""PythonScript application runner
"""

import sys, os
import code
from textwrap import dedent
import urlparse
import random

import demjson

from PyQt4 import QtCore, QtGui, QtWebKit


def random_password(length=20, charset=None):
    """Generate a random password of a given length"""
    if charset is None:
        charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    return "".join([random.choice(charset) for x in range(length)])


class Ui_HttpWidget(object):
    def setupUi(self, HttpWidget):
        #HttpWidget.setObjectName("HttpWidget")
        #HttpWidget.resize(1280, 1024)
        self.verticalLayout = QtGui.QVBoxLayout(HttpWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setMargin(0)
        self.webView = QtWebKit.QWebView(HttpWidget)
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.webView.setObjectName("webView")
        self.verticalLayout.addWidget(self.webView)
        self.retranslateUi(HttpWidget)
        QtCore.QMetaObject.connectSlotsByName(HttpWidget)

    def retranslateUi(self, HttpWidget):
        HttpWidget.setWindowTitle(QtGui.QApplication.translate("HttpWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))


class BrowserApp(QtGui.QMainWindow):
    browser_title = "PythonScript AppRunner"
    event_handlers = None
    action_handlers = None
    script_interpreter = None

    def __init__(self, parent=None):
        super(BrowserApp, self).__init__(parent)
        self.event_handlers = {}
        self.action_handlers = {}
        self.setWindowTitle(self.browser_title)
        self.layout().setMargin(0)
        self.resize(1280, 1024)
        #self.setWindowIcon( ... )

        self.ui = Ui_HttpWidget()
        self.ui.centralwidget = QtGui.QWidget(self)
        self.ui.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.ui.centralwidget)
        self.ui.setupUi(self.ui.centralwidget)

        self.ui.webView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.ui.webView.linkClicked.connect(self.linkClicked)
        self.ui.webView.loadFinished.connect(self.loadFinished)
        self.ui.webView.titleChanged.connect(self.titleChanged)

        QtCore.QMetaObject.connectSlotsByName(self)


    def loadApplication(self, url):
        self.ui.webView.setUrl(QtCore.QUrl(url))


    def loadFinished(self, status=None):
        """Callback for ``QWebVeiw.loadFinished()`` signal
        Prepares the page and executes all the Python scripts.
        """
        #print "Page loaded"
        page = self.ui.webView.page()
        main_frame = page.mainFrame()
        document = main_frame.documentElement()
        scripts = document.findAll('script')
        scripts_text = []
        for script in scripts.toList():
            ## TODO: Load external scripts too
            if script.attribute('type') == 'text/python':
                scripts_text.append(dedent(str(script.toPlainText())))

        def alert(text):
            print "@@ALERT@@: %s" % text
            QtGui.QMessageBox.warning(None, "Message from application", text)

        ## Script used to send events back to Python by simulating click
        ## on a link..
        ## This is an hack since QtWebKit doesn't provide anything to
        ## handle DOM events.
        document.evaluateJavaScript("""
        function simulatedEventHandler(event_tag, event) {
            var a = document.createElement('a');
            var evt2 = {
                type: event.type,
                clientX: event.clientX,
                clientY: event.clientY,
                offsetX: event.offsetX,
                offsetY: event.offsetY,
                screenX: event.screenX,
                screenY: event.screenY,
                pageX: event.pageX,
                pageY: event.pageY,

                target: event.target.id,
                currentTarget: event.currentTarget?event.currentTarget.id:null,
                relatedTarget: event.relatedTarget?event.relatedTarget.id:null,
                fromElement: event.fromElement?event.fromElement.id:null,

                defaultPrevented: event.defaultPrevented,
                detail: event.detail,
                eventPhase: event.eventPhase,
                isTrusted: event.isTrusted,

                bubbles: event.bubbles,
                button: event.button,
                cancelable: event.cancelable,

                charCode: event.charCode,
                keyCode: event.keyCode,
                metaKey: event.metaKey,
                ctrlKey: event.ctrlKey,
                altKey: event.altKey,
                shiftKey: event.shiftKey,

                timeStamp: event.timeStamp,

                wheelDelta: event.wheelDelta,
                wheelDeltaX: event.wheelDeltaX,
                wheelDeltaY: event.wheelDeltaY,

            };
            //NOTE: We still need a valid URL here!
            var href = "event://" + event.type + "/?event=" + encodeURIComponent(JSON.stringify(evt2)) + "&tag=" + encodeURIComponent(event_tag);
            a.href = encodeURI(href);
            a.innerHTML = " "; // The <a> requires some text
            a.style.display="none";
            document.body.appendChild(a);
            var evObj = document.createEvent('MouseEvents');
            evObj.initEvent('click', true, false);
            a.dispatchEvent(evObj);
            document.body.removeChild(a);
        };
        """)

        ## Prepare interpreter for running scripts
        context = {
            '__name__': '__pythonscript__',
            '__doc__': None,
            '__file__': __file__, ##TODO: Set path to the script/page as __file__

            ## Expose DOM objects in a more convenient way
            'document': document,
            'window': self,
            'frame': main_frame,

            ## Add utility functions
            'alert': alert,
        }

        ## Replace builtins with our customized module
        from custom_builtins import create_builtins
        context['__builtins__'] = create_builtins()

        ## Run script using a custom context
        self.script_interpreter = code.InteractiveInterpreter(context)
        self.runPythonScript(scripts_text)


    def titleChanged(self, title):
        """Handler for "title changed" events"""
        if title:
            self.setWindowTitle("%s - %s" % (title, self.browser_title))
        else:
            self.setWindowTitle(self.browser_title)


    def attachEventHandler(self, selector, event_type, callback=None):
        """Registers ``callback`` as DOM event handler for events of type
        ``event_type`` on objects matching ``selector``.

        ``callback`` will be called with an ``event`` object as only
        argument.

        .. warning::
           All this stuff is very hackerish, due to missing support for
           DOM events in QtWebKit: we have to simulate a link click
           from the javascript side, in order to get information
           on the event
        """
        event_tag = random_password(length=40)
        document = self.ui.webView.page().mainFrame().documentElement()
        js = """
        var elems=document.querySelectorAll("%(selector)s");
        for (var i=0; i<elems.length; i++) {
            elems[i].addEventListener("%(event_type)s", function(e){
                simulatedEventHandler("%(event_tag)s", e);});
        }
        """ % dict(event_tag=event_tag, selector=selector, event_type=event_type)
        document.evaluateJavaScript(js)
        self.event_handlers[event_tag] = callback

    def onAction(self, action, callback):
        if not self.action_handlers.has_key(action):
            self.action_handlers[action] = []
        self.action_handlers[action].append(callback)

    def runPythonScript(self, scripts):
        for sc_text in scripts:
            #exec sc_text in dict(globals(), **context), locals()
            self.script_interpreter.runcode(sc_text)

    def linkClicked(self, url):
        """Slot for "link clicked" signal.
        Processes events, actions or standard links.
        """
        url_str = str(url.toString())

        if url_str.startswith("event://"):
            ## This is an event. Emit a domEvent() signal and execute
            ## event handlers (if any)
            q = urlparse.parse_qs(url_str.split('?',1)[1])
            event = demjson.decode(urlparse.unquote(q['event'][0]))
            tag = q.get('tag')[0]
            self.domEvent.emit(event)
            if tag and self.event_handlers.has_key(tag) and callable(self.event_handlers[tag]):
                self.event_handlers[tag](event)

        elif url_str.startswith("action://"):
            ## Actions are in the format:
            ## action://<action-type>/<arg0>/<arg1>/../<argN>?<kw0>=<val0>&<kw1>=<val1>...&<kwN>=<valN>
            ## They should call a registered callback for <action-type> passing args/kwargs
            parsed = urlparse.urlparse(url_str)
            _path, _query = parsed.path, parsed.query
            if not _query and '?' in _path:
                ## urlparse only splits query for http:// urls
                _path, _query = _path.split('?', 1)
            action = parsed.netloc
            args = filter(None, _path.split('/'))
            kwargs = urlparse.parse_qs(_query)

            print "Running action=%r with args=%r and kwargs=%r" % (action, args, kwargs)
            if self.action_handlers.has_key(action):
                for fun in self.action_handlers[action]:
                    fun(*args, **kwargs)

        else:
            ## Open in browser
            ## TODO: Check for other protocols if needed..
            print "Opening %r in browser" % url_str
            #webbrowser.open(url_str)

    domEvent = QtCore.pyqtSignal('dict')

def handleEvent(event):
    """Generic events handler"""
    #print "--> EVENT SIGNAL: %r" % event
    pass


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = BrowserApp()

    url = 'file://%s' % os.path.abspath(os.path.join(os.path.dirname(__file__), 'pages', 'my-pythonscript-page.html'))
    myapp.loadApplication(url)

    myapp.domEvent.connect(handleEvent)

    myapp.show()
    sys.exit(app.exec_())

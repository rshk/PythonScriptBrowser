"""
:author: samu
:created: 5/30/12 1:33 AM
"""

import os, pickle
import cgi

## Hack to prevent some issues with undefined names..
if False:
    from pyqtbrowser.placeholders import *

def get_emails():
    return pickle.load(open(os.path.join(os.path.dirname(__file__), 'misc', 'data_emails.pickle'), 'r'))

def refresh_mail_list():
    emails_html = []
    for mailid, mail in enumerate(get_emails()):
        mail['id'] = "%d" % mailid
        mail['date'] = mail['date'].strftime('%F %T')
        mail = dict([map(lambda x: cgi.escape(str(x)), kv) for kv in mail.items()])
        emails_html += """
		<tr><td>%(id)s</td><td>%(date)s</td><td>%(email)s</td><td><a href="action://email-open/?mailid=%(id)s">%(subject)s</a></td></tr>
		""" % mail
    document.findFirst('#table-messages > tbody').setInnerXml("".join(emails_html));

def new_email():
    print "Will create a new email"

def open_email(mailid):
    print "Will show email %r" % mailid
    mail = get_emails()[int(mailid[0])]
    mail['date'] = mail['date'].strftime('%F %T')
    mail = dict([map(lambda x: cgi.escape(str(x)), kv) for kv in mail.items()])
    msgbox = document.findFirst('#message-display')
    msgbox.findFirst('.headers').setInnerXml("""
	<strong>From:</strong> %(email)s<br/>
	<strong>Date:</strong> %(date)s<br/>
	<strong>Subject:</strong> %(subject)s<br/>
	""" % mail)
    msgbox.findFirst('.body').setInnerXml(cgi.escape(mail['text']))
    msgbox.setStyleProperty('display', 'block')
    document.findFirst('#overlay').setStyleProperty('display', 'block')

def hide_message_overlay():
    document.findFirst('#message-display').setStyleProperty('display', 'none')
    document.findFirst('#overlay').setStyleProperty('display', 'none')

#window.attachEventHandler('#button-one', 'click', refresh_mail_list)
window.onAction('email-refresh', refresh_mail_list)
window.onAction('email-new', new_email)
window.onAction('email-open', open_email)
window.onAction('hide-message-overlay', hide_message_overlay)

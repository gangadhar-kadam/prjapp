# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes
from webnotes import _
from webnotes.utils import today

no_cache = True

def get_context():
	print "In the get_context of the email file^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^6"
	webnotes.errprint('in email')
	bean = webnotes.bean("Email Inbox", webnotes.form_dict.name)

	if bean.doc.raised_by != webnotes.session.user:
		return {
			"doc": {"name": "Not Allowed"}
		}
	else:
		return {
			"doc": bean.doc,
			"doclist": bean.doclist,
			"webnotes": webnotes,
			"utils": webnotes.utils
		}

@webnotes.whitelist()
def add_reply(email, message):
	if not message:
		raise webnotes.throw(_("Please write something"))
	
	bean = webnotes.bean("Email Inbox", email)
	if bean.doc.raised_by != webnotes.session.user:
		raise webnotes.throw(_("You are not allowed to reply to this email."), webnotes.PermissionError)
	
	from core.doctype.communication.communication import make
	make(content=message, sender=bean.doc.raised_by, subject = bean.doc.subject,
		doctype="Email Inbox", name=bean.doc.name,
		date=today())
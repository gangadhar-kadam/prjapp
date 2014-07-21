

# coding: utf-8
# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals
import webnotes
from webnotes.utils import cstr
from webnotes.model.doc import Document
# import time
import datetime

from utilities.transaction_base import TransactionBase
# from webnotes.utils import now, extract_email_id
#from support.doctype.email_inbox.gmail import Gmail
#from support.doctype.email_inbox.message import Message
#from support.doctype.email_inbox.mailbox import Mailbox

class DocType(TransactionBase):
	def __init__(self, doc, doclist=[]):
		self.doc = doc
		self.doclist = doclist
	
	def get_sender(self, comm):
		#webnotes.errprint('hi')
		return webnotes.conn.get_value('Email Settings',None,'support_email')

	def get_subject(self, comm):
		return '[' + self.doc.name + '] ' + (comm.subject or 'No Subject Specified')
	
	def get_content(self, comm):
		signature = webnotes.conn.get_value('Email Settings',None,'support_signature')
		content = comm.content
		# webnotes.errprint(content)
		if signature:
			content += '<p>' + signature + '</p>'
		return content
		
	def get_portal_page(self):
		return "email"
	
	def validate(self):
		self.update_status()
		self.set_lead_contact(self.doc.raised_by)
		
		if self.doc.status == "Closed":
			from webnotes.widgets.form.assign_to import clear
			clear(self.doc.doctype, self.doc.name)
				
	def set_lead_contact(self, email_id):
		import email.utils
		email_id = email.utils.parseaddr(email_id)
		if email_id:
			if not self.doc.lead:
				self.doc.lead = webnotes.conn.get_value("Lead", {"email_id": email_id})
			if not self.doc.contact:
				self.doc.contact = webnotes.conn.get_value("Contact", {"email_id": email_id})
				
			if not self.doc.company:		
				self.doc.company = webnotes.conn.get_value("Lead", self.doc.lead, "company") or \
					webnotes.conn.get_default("company")
	

	def update_status(self):
		status = webnotes.conn.get_value("Email Inbox", self.doc.name, "status")
		if self.doc.status!="Open" and status =="Open" and not self.doc.first_responded_on:
			self.doc.first_responded_on = now()
		if self.doc.status=="Closed" and status !="Closed":
			self.doc.resolution_date = now()
		if self.doc.status=="Open" and status !="Open":
			self.doc.resolution_date = ""

	#def on_update(self):
		#self.doc.flag='Read'
		#self.doc.save()


@webnotes.whitelist()
def set_flag(name):	
        webnotes.conn.sql("""Update `tabEmail Inbox` set flag='Read' where name='%s'"""%(name))
	webnotes.conn.sql("commit")


@webnotes.whitelist()
def set_status(name, status):
	st = webnotes.bean("Email Inbox", name)
	st.doc.status = status
	st.save()
		
def auto_close_emails():
	webnotes.conn.sql("""update `tabEmail Inbox` set status = 'Closed' 
		where status = 'Replied' 
		and date_sub(curdate(),interval 15 Day) > modified""")





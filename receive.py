# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import time
import _socket, poplib, imaplib
import frappe
from frappe import _
from frappe.utils import (extract_email_id, convert_utc_to_user_timezone, now,
	cint, cstr, strip, markdown)
from frappe.utils.scheduler import log
from email_reply_parser import EmailReplyParser
from email.header import decode_header
from frappe.utils.file_manager import get_random_filename

class EmailSizeExceededError(frappe.ValidationError): pass
class EmailTimeoutError(frappe.ValidationError): pass
class TotalSizeExceededError(frappe.ValidationError): pass
class LoginLimitExceeded(frappe.ValidationError): pass

class EmailServer:
	"""Wrapper for POP server to pull emails."""
	def __init__(self, args=None):
		self.setup(args)

	def setup(self, args=None):
		# overrride
		self.settings = args or frappe._dict()

	def check_mails(self):
		# overrride
		return True

	def process_message(self, mail):
		# overrride
		pass

	def connect(self):
		"""Connect to **Email Account**."""
		if cint(self.settings.use_imap):
			return self.connect_imap()
		else:
			return self.connect_pop()

	def connect_imap(self):
		"""Connect to IMAP"""
		try:
			if cint(self.settings.use_ssl):
				self.imap = Timed_IMAP4_SSL(self.settings.host, timeout=frappe.conf.get("pop_timeout"))
			else:
				self.imap = Timed_IMAP4(self.settings.host, timeout=frappe.conf.get("pop_timeout"))
			self.imap.login(self.settings.username, self.settings.password)
			# connection established!
			return True

		except _socket.error:
			# Invalid mail server -- due to refusing connection
			frappe.msgprint(_('Invalid Mail Server. Please rectify and try again.'))
			raise

		except Exception, e:
			frappe.msgprint(_('Cannot connect: {0}').format(str(e)))
			raise

	def connect_pop(self):
		#this method return pop connection
		try:
			if cint(self.settings.use_ssl):
				self.pop = Timed_POP3_SSL(self.settings.host, timeout=frappe.conf.get("pop_timeout"))
			else:
				self.pop = Timed_POP3(self.settings.host, timeout=frappe.conf.get("pop_timeout"))

			self.pop.user(self.settings.username)
			self.pop.pass_(self.settings.password)

			# connection established!
			return True

		except _socket.error:
			# log performs rollback and logs error in scheduler log
			log("receive.connect_pop")

			# Invalid mail server -- due to refusing connection
			frappe.msgprint(_('Invalid Mail Server. Please rectify and try again.'))
			raise

		except poplib.error_proto, e:
			if self.is_temporary_system_problem(e):
				return False

			else:
				frappe.msgprint(_('Invalid User Name or Support Password. Please rectify and try again.'))
				raise

	def get_messages(self):
		"""Returns new email messages in a list."""
		if not self.check_mails():
			return # nothing to do

		frappe.db.commit()

		if not self.connect():
			return []

		try:
			# track if errors arised
			self.errors = False
			self.latest_messages = []

			email_list = self.get_new_mails()
			num = num_copy = len(email_list)

			# WARNING: Hard coded max no. of messages to be popped
			if num > 20: num = 20

			# size limits
			self.total_size = 0
			self.max_email_size = cint(frappe.local.conf.get("max_email_size"))
			self.max_total_size = 5 * self.max_email_size

			for i, message_meta in enumerate(email_list):
				# do not pull more than NUM emails
				if (i+1) > num:
					break

				try:
					self.retrieve_message(message_meta, i+1)
				except (TotalSizeExceededError, EmailTimeoutError, LoginLimitExceeded):
					break

			# WARNING: Mark as read - message number 101 onwards from the pop list
			# This is to avoid having too many messages entering the system
			num = num_copy
			if not cint(self.settings.use_imap):
				if num > 100 and not self.errors:
					for m in xrange(101, num+1):
						self.pop.dele(m)

		except Exception, e:
			if self.has_login_limit_exceeded(e):
				pass

			else:
				raise

		finally:
			# no matter the exception, pop should quit if connected
			if cint(self.settings.use_imap):
				self.imap.logout()
			else:
				self.pop.quit()

		return self.latest_messages

	def get_new_mails(self):
		"""Return list of new mails"""
		if cint(self.settings.use_imap):
			self.imap.select("Inbox")
			response, message = self.imap.uid('search', None, "UNSEEN")
			email_list =  message[0].split()
		else:
			email_list = self.pop.list()[1]

		return email_list

	def retrieve_message(self, message_meta, msg_num=None):
		incoming_mail = None
		try:
			self.validate_message_limits(message_meta)

			if cint(self.settings.use_imap):
				status, message = self.imap.uid('fetch', message_meta, '(RFC822)')
				self.latest_messages.append(message[0][1])
			else:
				msg = self.pop.retr(msg_num)
				self.latest_messages.append(b'\n'.join(msg[1]))

		except (TotalSizeExceededError, EmailTimeoutError):
			# propagate this error to break the loop
			self.errors = True
			raise

		except Exception, e:
			if self.has_login_limit_exceeded(e):
				self.errors = True
				raise LoginLimitExceeded, e

			else:
				# log performs rollback and logs error in scheduler log
				log("receive.get_messages", self.make_error_msg(msg_num, incoming_mail))
				self.errors = True
				frappe.db.rollback()

				if not cint(self.settings.use_imap):
					self.pop.dele(msg_num)
				else:
					# mark as seen
					self.imap.uid('STORE', message_meta, '+FLAGS', '(\\SEEN)')
		else:
			if not cint(self.settings.use_imap):
				self.pop.dele(msg_num)
			else:
				# mark as seen
				self.imap.uid('STORE', message_meta, '+FLAGS', '(\\SEEN)')

	def has_login_limit_exceeded(self, e):
		return "-ERR Exceeded the login limit" in strip(cstr(e.message))

	def is_temporary_system_problem(self, e):
		messages = (
			"-ERR [SYS/TEMP] Temporary system problem. Please try again later.",
			"Connection timed out",
		)
		for message in messages:
			if message in strip(cstr(e.message)) or message in strip(cstr(getattr(e, 'strerror', ''))):
				return True
		return False

	def validate_message_limits(self, message_meta):
		# throttle based on email size
		if not self.max_email_size:
			return

		m, size = message_meta.split()
		size = cint(size)

		if size < self.max_email_size:
			self.total_size += size
			if self.total_size > self.max_total_size:
				raise TotalSizeExceededError
		else:
			raise EmailSizeExceededError

	def make_error_msg(self, msg_num, incoming_mail):
		error_msg = "Error in retrieving email."
		if not incoming_mail:
			try:
				# retrieve headers
				incoming_mail = Email(b'\n'.join(self.pop.top(msg_num, 5)[1]))
			except:
				pass

		if incoming_mail:
			error_msg += "\nDate: {date}\nFrom: {from_email}\nSubject: {subject}\n".format(
				date=incoming_mail.date, from_email=incoming_mail.from_email, subject=incoming_mail.subject)

		return error_msg

class Email:
	"""Wrapper for an email."""
	def __init__(self, content):
		"""Parses headers, content, attachments from given raw message.

		:param content: Raw message."""
		import email, email.utils
		import datetime


		self.raw = content
		self.mail = email.message_from_string(self.raw)

		self.text_content = ''
		self.html_content = ''
		self.attachments = []
		self.cid_map = {}
		self.parse()
		self.set_content_and_type()
		self.set_subject()

		# gmail mailing-list compatibility
		# use X-Original-Sender if available, as gmail sometimes modifies the 'From'
		_from_email = self.mail.get("X-Original-From") or self.mail["From"]

		self.from_email = extract_email_id(_from_email)
		self.from_real_name = email.utils.parseaddr(_from_email)[0]

		if self.mail["Date"]:
			utc = email.utils.mktime_tz(email.utils.parsedate_tz(self.mail["Date"]))
			utc_dt = datetime.datetime.utcfromtimestamp(utc)
			self.date = convert_utc_to_user_timezone(utc_dt).strftime('%Y-%m-%d %H:%M:%S')
		else:
			self.date = now()

	def parse(self):
		"""Walk and process multi-part email."""
		for part in self.mail.walk():
			self.process_part(part)

	def set_subject(self):
		"""Parse and decode `Subject` header."""
		import email.header
		_subject = email.header.decode_header(self.mail.get("Subject", "No Subject"))
		self.subject = _subject[0][0] or ""
		if _subject[0][1]:
			self.subject = self.subject.decode(_subject[0][1])
		else:
			# assume that the encoding is utf-8
			self.subject = self.subject.decode("utf-8")

		if not self.subject:
			self.subject = "No Subject"

	def set_content_and_type(self):
		self.content, self.content_type = '[Blank Email]', 'text/plain'
		if self.html_content:
			self.content, self.content_type = self.html_content, 'text/html'
		else:
			self.content, self.content_type = EmailReplyParser.parse_reply(self.text_content), 'text/plain'

	def process_part(self, part):
		"""Parse email `part` and set it to `text_content`, `html_content` or `attachments`."""
		content_type = part.get_content_type()
		if content_type == 'text/plain':
			self.text_content += self.get_payload(part)

		elif content_type == 'text/html':
			self.html_content += self.get_payload(part)

		elif content_type == 'message/rfc822':
			# sent by outlook when another email is sent as an attachment to this email
			self.show_attached_email_headers_in_content(part)

		elif part.get_filename():
			self.get_attachment(part)

	def show_attached_email_headers_in_content(self, part):
		# get the multipart/alternative message
		message = list(part.walk())[1]
		headers = []
		for key in ('From', 'To', 'Subject', 'Date'):
			value = cstr(message.get(key))
			if value:
				headers.append('{label}: {value}'.format(label=_(key), value=value))

		self.text_content += '\n'.join(headers)
		self.html_content += '<hr>' + '\n'.join('<p>{0}</p>'.format(h) for h in headers)

		if not message.is_multipart() and message.get_content_type()=='text/plain':
			# email.parser didn't parse it!
			text_content = self.get_payload(message)
			self.text_content += text_content
			self.html_content += markdown(text_content)

	def get_charset(self, part):
		"""Detect chartset."""
		charset = part.get_content_charset()
		if not charset:
			import chardet
			charset = chardet.detect(str(part))['encoding']

		return charset

	def get_payload(self, part):
		charset = self.get_charset(part)

		try:
			return unicode(part.get_payload(decode=True), str(charset), "ignore")
		except LookupError:
			return part.get_payload()

	def get_attachment(self, part):
		charset = self.get_charset(part)
		fcontent = part.get_payload(decode=True)

		if fcontent:
			content_type = part.get_content_type()
			fname = part.get_filename()
			if fname:
				try:
					fname = cstr(decode_header(fname)[0][0])
				except:
					fname = get_random_filename(content_type=content_type)
			else:
				fname = get_random_filename(content_type=content_type)

			self.attachments.append({
				'content_type': content_type,
				'fname': fname,
				'fcontent': fcontent,
			})

			cid = (part.get("Content-Id") or "").strip("><")
			if cid:
				self.cid_map[fname] = cid

	def save_attachments_in_doc(self, doc):
		"""Save email attachments in given document."""
		from frappe.utils.file_manager import save_file, MaxFileSizeReachedError
		saved_attachments = []

		for attachment in self.attachments:
			try:
				file_data = save_file(attachment['fname'], attachment['fcontent'],
					doc.doctype, doc.name, is_private=1)
				saved_attachments.append(file_data)

				if attachment['fname'] in self.cid_map:
					self.cid_map[file_data.name] = self.cid_map[attachment['fname']]

			except MaxFileSizeReachedError:
				# WARNING: bypass max file size exception
				pass
			except frappe.DuplicateEntryError:
				# same file attached twice??
				pass

		return saved_attachments

	def get_thread_id(self):
		"""Extract thread ID from `[]`"""
		import re
		l = re.findall('(?<=\[)[\w/-]+', self.subject)
		return l and l[0] or None


# fix due to a python bug in poplib that limits it to 2048
poplib._MAXLINE = 20480

class TimerMixin(object):
	def __init__(self, *args, **kwargs):
		self.timeout = kwargs.pop('timeout', 0.0)
		self.elapsed_time = 0.0
		self._super.__init__(self, *args, **kwargs)
		if self.timeout:
			# set per operation timeout to one-fifth of total pop timeout
			self.sock.settimeout(self.timeout / 5.0)

	def _getline(self, *args, **kwargs):
		start_time = time.time()
		ret = self._super._getline(self, *args, **kwargs)

		self.elapsed_time += time.time() - start_time
		if self.timeout and self.elapsed_time > self.timeout:
			raise EmailTimeoutError

		return ret

	def quit(self, *args, **kwargs):
		self.elapsed_time = 0.0
		return self._super.quit(self, *args, **kwargs)

class Timed_POP3(TimerMixin, poplib.POP3):
	_super = poplib.POP3

class Timed_POP3_SSL(TimerMixin, poplib.POP3_SSL):
	_super = poplib.POP3_SSL
class Timed_IMAP4(TimerMixin, imaplib.IMAP4):
	_super = imaplib.IMAP4

class Timed_IMAP4_SSL(TimerMixin, imaplib.IMAP4_SSL):
	_super = imaplib.IMAP4_SSL

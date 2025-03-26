# -*- coding: utf-8 -*-
# Copyright (c) 2023, Mututa Paul and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

# ..............imports to MOMO.................
from frappe.model.document import Document
from frappe import _, throw, msgprint
from frappe.utils import nowdate

import six
from six import string_types
import json
import base64
import uuid
import requests

# ..............imports to MOMO.................

class MomoUserSettings(Document):
	def before_save(self):
		self.xref_user  = str(uuid.uuid4())
		# CREATE USER
		endpont_userurl = "https://sandbox.momodeveloper.mtn.com/v1_0/apiuser"
		user_payload = {
			"providerCallbackHost": self.providercallbackhost
		}
		headers_user = {
			"X-Reference-Id":self.xref_user,
			"Content-Type":"application/json",
			"Ocp-Apim-Subscription-Key":self.ocp_user
		}
		response_user = requests.post(endpont_userurl, headers=headers_user, json=user_payload)

		# END CREATE 
		# creete API

		endpoint_api_keyurl = f"https://sandbox.momodeveloper.mtn.com/v1_0/apiuser/{self.xref_user}/apikey"

		headers_apikey = {
			 "Ocp-Apim-Subscription-Key": self.ocp_user
		}
		response_apikey = requests.post(endpoint_api_keyurl, headers=headers_apikey)
		final = response_apikey.json()
		apikey = json.dumps(final)
		api_key = final["apiKey"]
		self.momo_api_key = api_key
		# frappe.msgprint(_("Thanks you for regestering for MTN MOMO Pay"))	
		# creete API
		


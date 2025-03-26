# -*- coding: utf-8 -*-
# Copyright (c) 2023, Mututa Paul and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

# ..............imports to EFRIS.................
from frappe.model.document import Document
from frappe import _, throw, msgprint
from frappe.utils import nowdate

import six
from six import string_types
import json
import base64
import uuid
import requests

# ..............imports to EFRIS.................


# endpoint_url = "https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay"

class MtnMomoPay(Document):
	def before_save(self): 
	    # CREATED USER  FRO THE TOKEN
		ocp_user = frappe.get_list("Momo User Settings", ["ocp_user"])
		momo_api_key = frappe.get_list("Momo User Settings", ["momo_api_key"])
		xref_user = frappe.get_list("Momo User Settings", ["xref_user"])
		# CREATED USER THE TOKEN
		
		endpoint_token = "https://sandbox.momodeveloper.mtn.com/collection/token/"
		api_user = xref_user
		api_key = momo_api_key
		string_to_encode  = api_user[0]['xref_user'] + ":" + api_key[0]['momo_api_key']
		encoded_string = base64.b64encode(string_to_encode.encode()).decode()
		
		headers_token = {
			"Authorization":f"Basic {encoded_string}",
			"Ocp-Apim-Subscription-Key":f"{ocp_user[0]['ocp_user']}"
		}

		response_token = requests.post(endpoint_token, headers=headers_token)
	
		final_token = response_token.json()
		access_token = final_token["access_token"]
		self.access_token = access_token

		# end of creating atoken	

		# Set the endpoint URL and headers

		self.xref_user  = str(uuid.uuid4())
		self.authorization = f"Bearer {self.access_token}"
		endpoint_url = "https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay"
		headers = {
 			"Authorization": f"Bearer {self.access_token}",
		    "X-Reference-Id": self.xref_user,
		    "X-Target-Environment": "sandbox",
		    "Content-Type": "application/json",
		    "Ocp-Apim-Subscription-Key": f"{ocp_user[0]['ocp_user']}"
		}

		# Set the payload
		payload = {
		    "amount": self.amount,
		    "currency": self.currency,
		    "externalId": "12345678",
		    "payer": {
		        "partyIdType": "MSISDN",
		        "partyId": self.phone_number
	    },
	    "payerMessage": "Payment for goods",
	    "payeeNote": "Thank you for your payment"
		}

		# Make the request
		response = requests.post(endpoint_url, headers=headers, json=payload)

		# Print the response
		frappe.msgprint(_("Thanks your Data has been sent to Efris" + response.text))
		# print(response.text)
	
	def on_submit(self):
		
		# Set the endpoint URL and headers
		ocp = frappe.get_list("Byoosi Momo User Settings", ["ocp_user"])[0]['ocp_user']
		endpoint_url = f"https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay/{self.xref_user}"
		headers = {
		    "Authorization": f"Bearer {self.access_token}",
		    "X-Target-Environment": "sandbox",
		    "Ocp-Apim-Subscription-Key": ocp
		}

		# Make the request
		response = requests.get(endpoint_url, headers=headers)
		status = json.dumps(response.json())
		self.test_field = status['status']
		frappe.msgprint(_("Thanks your Data has been sent to Efris" + json.dumps(response.json())))
		
		
	







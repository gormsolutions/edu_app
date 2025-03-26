# -*- coding: utf-8 -*-
# Copyright (c) 2023, Mututa Paul and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests

class MoneyCollectionPayment(Document):
	def make_mtn_mobile_money_collection_payment(self, phone_number, amount):
		# Set the endpoint 
		random_uuid = frappe.generate_hash()
		Subscription_Key = "61c20850dc6b4224bb8ad9ab0c762925"
		endpont_api_ky_url = "https://sandbox.momodeveloper.mtn.com/v1_0/apiuser/x-Reference-Id/apikey"
		endpoint_url = "https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay"
		
		headers = {
			"Authorization":"Bearer f{acess_token}",
			"X-Reference-Id": random_uuid,
    	    "X-Target-Environment": "sandbox",
    	    "Content-Type": "application/json",
    	    "Ocp-Apim-Subscription-Key": Subscription_Key
		}
		headers_apikey = {

    	    "Ocp-Apim-Subscription-Key": Subscription_Key
		}	
		payload = {
			"amount": self.amount,
    	    "currency": "UGX",
    	    "externalId": "12345678",
    	    "payer": {
        	    "partyIdType": "MSISDN",
        	    "partyId": self.phone_number
    	    },
        	"payeeNote": "Payment for goods and services"

		}
		response = requests.post(endpoint_url, headers=headers, json=payload)
	






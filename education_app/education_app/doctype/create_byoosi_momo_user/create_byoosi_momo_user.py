# -*- coding: utf-8 -*-
# Copyright (c) 2023, Mututa Paul and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

# ..............create user to mtn momo.................
import requests

def before_save(phone_number, amount):
    # Set the endpoint URL
    endpoint_url = "https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay"
    
    # Set the headers
    headers = {
        "X-Reference-Id": "your_reference_id",
        "X-Target-Environment": "sandbox",
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": "your_subscription_key"
    }
    
    # Set the payload
    payload = {
        "amount": amount,
        "currency": "UGX",
        "externalId": "your_external_id",
        "payer": {
            "partyIdType": "MSISDN",
            "partyId": phone_number
        },
        "payeeNote": "Payment for goods and services"
    }
    
    # Make the request
    response = requests.post(endpoint_url, headers=headers, json=payload)
    
    # Return the response
    # return response.json()

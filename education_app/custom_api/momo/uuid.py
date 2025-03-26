import requests
import uuid
import frappe

@frappe.whitelist(allow_guest=True)  # Allow API call from outside
def create_api_user():
    reference_id = str(uuid.uuid4())  # Generate a unique UUID
    subscription_key = "61c20850dc6b4224bb8ad9ab0c762925"  # Replace with actual key

    url = "https://sandbox.momodeveloper.mtn.com/v1_0/apiuser"

    headers = {
        "X-Reference-Id": reference_id,
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": subscription_key,
    }

    body = {
        "providerCallbackHost": "localhost"  # Replace with your domain
    }

    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # Raise an error if the request fails

        frappe.logger().info(f"MTN Momo API User Created: {reference_id}")

        return {
            "status": response.status_code,
            "message": "API User Created Successfully",
            "reference_id": reference_id
        }

    except requests.exceptions.RequestException as e:
        frappe.logger().error(f"Error creating API user: {str(e)}")
        return {"error": str(e)}

import requests
import uuid
import frappe
from requests.auth import HTTPBasicAuth

@frappe.whitelist(allow_guest=True)
def create_get_api_user_generate_key_and_get_token():
    """
    Create an API user, fetch its details, generate an API key, and get an access token.
    """
    reference_id = str(uuid.uuid4())  # Generate a unique UUID
    subscription_key = "61c20850dc6b4224bb8ad9ab0c762925"  # Replace with your MTN Momo API subscription key

    url_create = "https://sandbox.momodeveloper.mtn.com/v1_0/apiuser"
    url_get = f"https://sandbox.momodeveloper.mtn.com/v1_0/apiuser/{reference_id}"
    url_generate_key = f"https://sandbox.momodeveloper.mtn.com/v1_0/apiuser/{reference_id}/apikey"
    url_get_token = "https://sandbox.momodeveloper.mtn.com/collection/token/"

    headers = {
        "X-Reference-Id": reference_id,
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": subscription_key,
    }

    body = {
        "providerCallbackHost": "https://your-callback-url.com"  # Replace with your actual callback URL
    }

    try:
        # Step 1: Create API User
        response_create = requests.post(url_create, json=body, headers=headers)
        response_create.raise_for_status()

        # Step 2: Fetch API User Details
        response_get = requests.get(url_get, headers=headers)
        response_get.raise_for_status()
        user_details = response_get.json()

        # Step 3: Generate API Key
        response_key = requests.post(url_generate_key, headers=headers)
        response_key.raise_for_status()
        api_key = response_key.json().get("apiKey")

        # Step 4: Get Access Token (Basic Auth: username=reference_id, password=api_key)
        headers_token = {
            "Ocp-Apim-Subscription-Key": subscription_key,
        }

        response_token = requests.post(
            url_get_token,
            headers=headers_token,
            auth=HTTPBasicAuth(reference_id, api_key)
        )

        response_token.raise_for_status()
        token_data = response_token.json()
        access_token = token_data.get("access_token")
        token_type = token_data.get("token_type")
        expires_in = token_data.get("expires_in")

        # Log and return the results
        frappe.logger().info(f"API User Created, Details Fetched, API Key Generated, and Token Retrieved: {reference_id}")

        return {
            "status": response_create.status_code,
            "message": "API User Created Successfully",
            "reference_id": reference_id,
            "user_details": user_details,
            "api_key": api_key,
            "access_token": access_token,
            "token_type": token_type,
            "expires_in": expires_in,
        }

    except requests.exceptions.RequestException as e:
        frappe.logger().error(f"Error in API User Process: {str(e)}")
        return {"error": str(e)}

#https://www.paymee.tn/paymee-integration-with-redirection/
#https://www.paymee.tn/swagger.html
#https://www.paymee.tn/
import requests
import hashlib
import json
from django.conf import settings

PAYMEE_SANDBOX_URL = "https://sandbox.paymee.tn/api/v2/payments/create"
PAYMEE_LIVE_URL = "https://app.paymee.tn/api/v2/payments/create"
#GATEWAY_URL = "https://app.paymee.tn/api/v2/payments/create"

API_URL = PAYMEE_LIVE_URL if not settings.DEBUG else PAYMEE_SANDBOX_URL

def generate_paymee_payment(amount, note, first_name, last_name, email, phone, return_url, cancel_url, webhook_url, order_id=None):
                     
    """
    Initiates a payment session using the Paymee Payments API.

    This utility sends a POST request to Paymee with user and payment details to create a transaction session. 
    If successful, it returns a Paymee-hosted payment URL that you can redirect the user to for completing the payment.

    Unlike Flouci, Paymee requires collecting the user's personal info (name, email, phone) before initiating the request.

    After the user interacts with the Paymee page, Paymee will send a webhook (server-to-server POST) to a provided 
    `webhook_url` with the payment result (success or failure). You are expected to implement a view to handle this callback.

    Args:
        amount (float): Payment amount. Example: 220.25
        note (str): A note or description for the payment. Example: "Order #123"
        first_name (str): Buyer's first name. Example: "John"
        last_name (str): Buyer's last name. Example: "Doe"
        email (str): Buyer's email address. Example: "test@paymee.tn"
        phone (str): Buyer's phone number. Example: "+21611222333"
        return_url (str): URL to redirect the user after successful payment. Example: "https://www.mysite.tn/payment/finished"
        cancel_url (str): URL to redirect the user if the payment is canceled. Example: "https://www.mysite.tn/payment/canceled"
        webhook_url (str): URL Paymee will notify after payment completion. Must be CSRF-exempt.
        order_id (str, optional): A unique order reference from your system. Example: "269447"

    Returns:
        str: A Paymee payment URL (e.g., https://paymee.tn/gateway/<token>) where the user can finalize the payment.

    Raises:
        ValueError: If the API call fails or returns an invalid response.

    Notes:
        - You must create and configure a Paymee merchant account as described in the Paymee API documentation.
        - The `webhook_url` must point to a Django view that handles POST requests and validates the `check_sum`.
        - This function does not handle webhook processing or payment verification — it only starts the session.
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {settings.PAYMEE_API_KEY}"
    }
    payload = {
        "amount": amount,
        "note": note,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "return_url": return_url,
        "cancel_url": cancel_url,
        "webhook_url": webhook_url,
    }
    if order_id:
        payload["order_id"] = order_id

    resp = requests.post(API_URL, data=json.dumps(payload), headers=headers)
    data = resp.json() # or json.loads(resp.text)
    if data.get("status") and data.get("data", {}).get("payment_url"):
        return data["data"]["payment_url"]
    raise ValueError(f"Paymee initiation error: {data}")



def verify_webhook(payload):
    """
    Verifies Paymee webhook payload integrity using check_sum.
    check_sum = md5(token + payment_status + API_KEY)
    payload must be json.loads(payload) first
    
    Args:
        payload (dict): The webhook data received from Paymee.
    
    Returns:
        bool: True if the checksum is valid and the data is authentic.
    """
    token = payload.get("token", "")
    status_bool = payload.get("payment_status")
    status_int = "1" if status_bool else "0"
    api_key = settings.PAYMEE_API_KEY

    # Rebuild the expected checksum string: token + 1 or 0 + API_KEY
    expected = hashlib.md5(f"{token}{status_int}{api_key}".encode()).hexdigest()

    # Compare the calculated checksum to the one provided by Paymee
    return expected == payload.get("check_sum", "")



"""
Usage example:

# views.py
from django.shortcuts import redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.payments.paymee import initiate_payment, verify_webhook

def start_payment(request):
    url = initiate_payment(
        amount=220.25,
        note="Order #123",
        first_name="John", last_name="Doe",
        email="john@example.com", phone="+21611222333",
        return_url=request.build_absolute_uri("/pay/success/"),
        cancel_url=request.build_absolute_uri("/pay/cancel/"),
        webhook_url=request.build_absolute_uri("/pay/webhook/"),
        order_id="ORD123"
    )
    return redirect(url)

@csrf_exempt
def paymee_webhook(request):
    payload = json.loads(request.body)
    if verify_webhook(payload):
        # save transaction status based on payload["payment_status"]
        return HttpResponse(status=200)
    return HttpResponse(status=400)

"""
#https://flouci.stoplight.io/docs/flouci-payment-apis/455b330c10e0d-en-flouci-payment-api
import requests
import json
from django.conf import settings


# This function only creates a payment "template" or session request:
# - You specify yourself as the receiver (via your app credentials: settings.FLOUCI_APP_TOKEN, settings.FLOUCI_APP_SECRET).
# - You define the payment amount and provide redirect URLs.
# 
# If Flouci approves the request (i.e., data['result']['success'] is True),
# it returns a secure payment link (you must handle the first redirection in the view then forget).
# 
# The user is then redirected to that link (a flouci.com form) to complete payment.
# Your platform does NOT handle or collect any payment credentials.
# 
# Flouci is responsible for processing the transaction and will redirect (that's why no credit card params)
# Response: the user to the success or fail URL you provided based on the outcome.


def generate_flouci_payment(amount, success_link, fail_link, tracking_id=None, accept_card=True, timeout_secs=1200):
    """
    Initiates a payment session using the Flouci Payments API.

    This function sends a payment request to Flouci and returns a payment URL 
    that users can be redirected to for completing the transaction.

    Args:
        amount (int or str): The payment amount in millimes (e.g., 5000 = 5 TND).
        success_link (str): URL to redirect the user to after a successful payment.
        fail_link (str): URL to redirect the user to if the payment fails or is canceled.
        tracking_id (str, optional): An internal identifier for tracking the transaction.
        accept_card (bool): Whether to allow card payments. Defaults to True.
        timeout_secs (int): Session expiration time in seconds. Defaults to 1200.

    Returns:
        str: A Flouci-hosted URL where the user can complete the payment.

    Raises:
        ValueError: If the API call fails or the response is malformed.

    Notes:
        You must define `FLOUCI_APP_TOKEN` and `FLOUCI_APP_SECRET` in your Django settings.
        To get credentials, register at https://www.flouci.com and upgrade to a Developer API account.

    Usage:
            def start_payment(request):
                try:
                    payment_url = generate_flouci_payment(
                        amount=100,
                        success_link="https://my-website.com/payment/success/",
                        fail_link="https://my-website.com/payment/fail/",
                        tracking_id="order-123"
                    )
                    return redirect(payment_url)
                except ValueError as e:
                    return JsonResponse({"error": str(e)}, status=500)
    """
    url = "https://developers.flouci.com/api/generate_payment"

    payload = {
        "app_token": settings.FLOUCI_APP_TOKEN,
        "app_secret": settings.FLOUCI_APP_SECRET,
        "accept_card": str(accept_card).lower(),
        "amount": str(amount),
        "success_link": success_link,
        "fail_link": fail_link,
        "session_timeout_secs": timeout_secs,
        "developer_tracking_id": tracking_id or ""
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    try:
        data = response.json()
        if 'result' in data and data['result'].get('success'):
            return data['result']['link']
        raise ValueError(f"Payment creation failed: {data}")
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid response from Flouci: {str(e)}\nRaw response: {response.text}")





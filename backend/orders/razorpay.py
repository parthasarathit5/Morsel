"""Razorpay integration using only the Python standard library.

Uses https://api.razorpay.com/v1 with HTTP Basic auth.
Set RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET (and optionally
RAZORPAY_WEBHOOK_SECRET) in the environment to go live; without them
the app runs in DEMO mode where payments are simulated.
"""

import base64
import hashlib
import hmac
import json
import urllib.error
import urllib.request

from django.conf import settings


class RazorpayError(Exception):
    """Raised when the Razorpay API cannot be reached or returns an error."""


def _auth_header() -> str:
    raw = f'{settings.RAZORPAY_KEY_ID}:{settings.RAZORPAY_KEY_SECRET}'.encode()
    return f'Basic {base64.b64encode(raw).decode()}'


def _request(method: str, path: str, payload: dict | None = None) -> dict:
    url = f'https://api.razorpay.com/v1{path}'
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            'Authorization': _auth_header(),
            'Content-Type': 'application/json',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors='replace')[:300]
        raise RazorpayError(f'Razorpay API error {exc.code}: {detail}') from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RazorpayError(f'Cannot reach Razorpay: {exc}') from exc


def create_order(amount_paise: int, receipt: str, notes: dict | None = None) -> dict:
    """Create a Razorpay order. Returns the API response dict."""
    return _request(
        'POST',
        '/orders',
        {
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': receipt,
            'notes': notes or {},
        },
    )


def verify_checkout_signature(
    razorpay_order_id: str, razorpay_payment_id: str, signature: str
) -> bool:
    """Verify the signature returned by Razorpay Checkout."""
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f'{razorpay_order_id}|{razorpay_payment_id}'.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature or '')


def verify_webhook_signature(raw_body: bytes, signature: str) -> bool:
    """Verify the X-Razorpay-Signature header on webhooks."""
    secret = settings.RAZORPAY_WEBHOOK_SECRET or settings.RAZORPAY_KEY_SECRET
    if not secret:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or '')

"""SMS provider integration (Sparrow) — Block 3B.

The provider is abstracted behind :func:`send_sms` so tests can monkeypatch
it without touching the network. In development the function logs and
returns ``True`` without calling Sparrow if no API key is configured.

Inbound parsing
---------------
A merchant forwards the customer's QR string via SMS. The body may be the
raw QR (``v1.<body>.<sig>``) optionally prefixed with a keyword such as
``PAY``. :func:`extract_qr_payload` normalizes that.
"""
from __future__ import annotations

import logging
import re

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

SPARROW_ENDPOINT = "https://api.sparrowsms.com/v2/sms/"

_QR_RE = re.compile(r"(v1\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+)")


class SMSParseError(ValueError):
    """Raised when an inbound SMS body does not contain a recognisable QR."""


def extract_qr_payload(text: str) -> str:
    """Pull the QR payload out of an SMS body.

    Accepts the raw payload or a prefix like ``PAY <payload>``.
    """
    if not text:
        raise SMSParseError("empty SMS body")
    match = _QR_RE.search(text.strip())
    if not match:
        raise SMSParseError("no QR payload found in SMS")
    return match.group(1)


async def send_sms(to: str, message: str) -> bool:
    """Send an SMS via Sparrow. Returns True on success.

    In development (no API key), this becomes a no-op that just logs.
    """
    if not settings.SPARROW_API_KEY:
        logger.info("SMS (dev no-op) -> %s: %s", to, message)
        return True

    payload = {
        "token": settings.SPARROW_API_KEY,
        "from": settings.SPARROW_SENDER_ID,
        "to": to,
        "text": message,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            resp = await http.post(SPARROW_ENDPOINT, data=payload)
        if resp.status_code // 100 != 2:
            logger.error("Sparrow send failed %s: %s", resp.status_code, resp.text)
            return False
    except httpx.HTTPError:
        logger.exception("Sparrow send raised")
        return False
    return True


def format_confirmation(*, transaction_id: str, amount, merchant_name: str) -> str:
    return (
        f"Offline Sewa: payment of Rs. {amount} to {merchant_name} confirmed. "
        f"Ref {transaction_id}."
    )


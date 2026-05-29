"""SMS provider integration + inbound message parsing (Block 3B).

Inbound text format expected from shopkeepers:

    PAY <merchant_id> <qr_payload>

Anything else raises ``InvalidSMSFormat``. Outbound delivery uses the
Sparrow SMS HTTP API when ``SPARROW_API_KEY`` is configured; otherwise it
logs and returns ``False`` so dev environments keep working without
network access.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

SPARROW_ENDPOINT = "https://api.sparrowsms.com/v2/sms/"
_CMD_RE = re.compile(r"^\s*PAY\s+(\S+)\s+(\S+)\s*$", re.IGNORECASE)


class SMSServiceError(Exception):
    code = "sms_error"
    http_status = 400


class InvalidSMSFormat(SMSServiceError):
    code = "invalid_sms_format"
    http_status = 400


@dataclass(slots=True)
class ParsedPayment:
    merchant_id: str
    qr_payload: str


def parse_payment_sms(text: str) -> ParsedPayment:
    """Extract merchant_id + qr_payload from an inbound SMS body."""
    if not text:
        raise InvalidSMSFormat("empty SMS body")
    m = _CMD_RE.match(text)
    if not m:
        raise InvalidSMSFormat(
            "expected 'PAY <merchant_id> <qr_payload>'"
        )
    merchant_id, qr_payload = m.group(1), m.group(2)
    return ParsedPayment(merchant_id=merchant_id, qr_payload=qr_payload)


async def send_sms(to: str, message: str) -> bool:
    """Send an outgoing SMS. Returns True on provider success.

    No-op (returns False) if no API key is configured — keeps local dev
    and tests offline-safe.
    """
    if not settings.SPARROW_API_KEY:
        log.info("sms.send skipped (no SPARROW_API_KEY): to=%s msg=%s", to, message)
        return False

    payload = {
        "token": settings.SPARROW_API_KEY,
        "from": settings.SPARROW_SENDER_ID,
        "to": to,
        "text": message,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            r = await http.post(SPARROW_ENDPOINT, data=payload)
        if r.status_code >= 400:
            log.warning("sms.send failed status=%s body=%s", r.status_code, r.text)
            return False
        return True
    except httpx.HTTPError as e:
        log.warning("sms.send transport error: %s", e)
        return False


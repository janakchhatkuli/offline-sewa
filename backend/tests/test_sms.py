"""SMS flow + settlement tests — Block 3B."""
from decimal import Decimal

import pytest

from app.services import sms_service


# --- Unit: SMS body parsing -------------------------------------------------
def test_extract_qr_raw_payload():
    payload = "v1.AAAA.BBBB"
    assert sms_service.extract_qr_payload(payload) == payload


def test_extract_qr_with_prefix():
    payload = "v1.AAAA-_.BBBB_-"
    assert sms_service.extract_qr_payload(f"PAY {payload}") == payload


def test_extract_qr_missing():
    with pytest.raises(sms_service.SMSParseError):
        sms_service.extract_qr_payload("hello there")


def test_extract_qr_empty():
    with pytest.raises(sms_service.SMSParseError):
        sms_service.extract_qr_payload("")


# --- SMS webhook ------------------------------------------------------------
@pytest.mark.asyncio
async def test_confirm_payment_success(client, seeded, monkeypatch):
    sent = {}

    async def _fake_send(to, message):
        sent["to"] = to
        sent["message"] = message
        return True

    monkeypatch.setattr(sms_service, "send_sms", _fake_send)

    create = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "75.00"},
    )
    qr = create.json()["qr_payload"]

    r = await client.post(
        "/api/v1/sms/confirm-payment",
        json={"from": "+9779800000002", "text": f"PAY {qr}", "message_id": "m1"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "pending_settlement"
    assert data["customer_id"] == "cust_test01"
    assert data["merchant_id"] == "merch_test01"
    assert Decimal(data["amount"]) == Decimal("75.00")
    assert data["sms_sent"] is True
    assert sent["to"] == "+9779800000002"
    assert "75.00" in sent["message"]


@pytest.mark.asyncio
async def test_confirm_payment_unknown_sender(client, seeded):
    r = await client.post(
        "/api/v1/sms/confirm-payment",
        json={"from": "+9770000000000", "text": "PAY v1.AAA.BBB"},
    )
    assert r.status_code == 404
    assert r.json()["detail"]["error"] == "merchant_not_found"


@pytest.mark.asyncio
async def test_confirm_payment_malformed_body(client, seeded):
    r = await client.post(
        "/api/v1/sms/confirm-payment",
        json={"from": "+9779800000002", "text": "hello, no QR here"},
    )
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "malformed_sms"


@pytest.mark.asyncio
async def test_confirm_payment_replay_rejected(client, seeded, monkeypatch):
    async def _fake_send(to, message):
        return True

    monkeypatch.setattr(sms_service, "send_sms", _fake_send)

    create = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "20.00"},
    )
    qr = create.json()["qr_payload"]

    r1 = await client.post(
        "/api/v1/sms/confirm-payment",
        json={"from": "+9779800000002", "text": qr},
    )
    assert r1.status_code == 200

    r2 = await client.post(
        "/api/v1/sms/confirm-payment",
        json={"from": "+9779800000002", "text": qr},
    )
    assert r2.status_code == 409
    assert r2.json()["detail"]["error"] == "nonce_already_used"


# --- Settlement -------------------------------------------------------------
@pytest.mark.asyncio
async def test_settle_success(client, seeded, monkeypatch):
    async def _fake_send(to, message):
        return True

    monkeypatch.setattr(sms_service, "send_sms", _fake_send)

    # Two separate payments → both should land as pending.
    for amt in ("30.00", "45.50"):
        create = await client.post(
            "/api/v1/transactions/create-offline-qr",
            json={"customer_id": "cust_test01", "amount": amt},
        )
        qr = create.json()["qr_payload"]
        v = await client.post(
            "/api/v1/transactions/verify-offline-qr",
            json={"merchant_id": "merch_test01", "qr_payload": qr},
        )
        assert v.status_code == 200

    pre = await client.get("/api/v1/merchants/merch_test01")
    assert Decimal(pre.json()["pending_settlement"]) == Decimal("75.50")

    r = await client.post("/api/v1/merchants/merch_test01/settle")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["settled_count"] == 2
    assert Decimal(data["settled_amount"]) == Decimal("75.50")
    assert Decimal(data["pending_settlement"]) == Decimal("0.00")
    assert Decimal(data["settled_balance"]) == Decimal("75.50")

    post = await client.get("/api/v1/merchants/merch_test01")
    assert Decimal(post.json()["pending_settlement"]) == Decimal("0.00")
    assert Decimal(post.json()["settled_balance"]) == Decimal("75.50")


@pytest.mark.asyncio
async def test_settle_nothing_pending(client, seeded):
    r = await client.post("/api/v1/merchants/merch_test01/settle")
    assert r.status_code == 409
    assert r.json()["detail"]["error"] == "nothing_to_settle"


@pytest.mark.asyncio
async def test_settle_merchant_missing(client, seeded):
    r = await client.post("/api/v1/merchants/merch_nope/settle")
    assert r.status_code == 404


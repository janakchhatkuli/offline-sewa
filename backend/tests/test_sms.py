"""SMS flow tests — Block 3B."""
from decimal import Decimal

import pytest

from app.services import sms_service


def test_parse_payment_sms_ok():
    parsed = sms_service.parse_payment_sms("PAY merch_test01 v1.body.sig")
    assert parsed.merchant_id == "merch_test01"
    assert parsed.qr_payload == "v1.body.sig"


def test_parse_payment_sms_case_insensitive():
    parsed = sms_service.parse_payment_sms("  pay merch_x v1.a.b  ")
    assert parsed.merchant_id == "merch_x"


def test_parse_payment_sms_rejects_garbage():
    with pytest.raises(sms_service.InvalidSMSFormat):
        sms_service.parse_payment_sms("hello there")


@pytest.mark.asyncio
async def test_sms_confirm_payment_success(client, seeded):
    create = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "75.00"},
    )
    qr = create.json()["qr_payload"]

    r = await client.post(
        "/api/v1/sms/confirm-payment",
        json={"from": "+9779800000002", "text": f"PAY merch_test01 {qr}"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "pending_settlement"
    assert data["merchant_id"] == "merch_test01"
    assert Decimal(data["amount"]) == Decimal("75.00")
    assert data["notified"] is False  # no SPARROW_API_KEY in tests


@pytest.mark.asyncio
async def test_sms_confirm_payment_invalid_format(client, seeded):
    r = await client.post(
        "/api/v1/sms/confirm-payment",
        json={"from": "+9779800000002", "text": "BALANCE"},
    )
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "invalid_sms_format"


@pytest.mark.asyncio
async def test_sms_confirm_payment_replay_rejected(client, seeded):
    create = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "20.00"},
    )
    qr = create.json()["qr_payload"]
    body = {"from": "+9779800000002", "text": f"PAY merch_test01 {qr}"}

    r1 = await client.post("/api/v1/sms/confirm-payment", json=body)
    assert r1.status_code == 200
    r2 = await client.post("/api/v1/sms/confirm-payment", json=body)
    assert r2.status_code == 409
    assert r2.json()["detail"]["error"] == "nonce_already_used"


@pytest.mark.asyncio
async def test_settle_merchant_flow(client, seeded):
    # two QR payments
    for amt in ("30.00", "20.00"):
        c = await client.post(
            "/api/v1/transactions/create-offline-qr",
            json={"customer_id": "cust_test01", "amount": amt},
        )
        qr = c.json()["qr_payload"]
        v = await client.post(
            "/api/v1/transactions/verify-offline-qr",
            json={"merchant_id": "merch_test01", "qr_payload": qr},
        )
        assert v.status_code == 200

    r = await client.post("/api/v1/merchants/merch_test01/settle")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["settled_count"] == 2
    assert Decimal(data["settled_amount"]) == Decimal("50.00")
    assert Decimal(data["pending_settlement"]) == Decimal("0.00")
    assert Decimal(data["settled_balance"]) == Decimal("50.00")


@pytest.mark.asyncio
async def test_settle_merchant_nothing_pending(client, seeded):
    r = await client.post("/api/v1/merchants/merch_test01/settle")
    assert r.status_code == 409
    assert r.json()["detail"]["error"] == "nothing_to_settle"


@pytest.mark.asyncio
async def test_settle_merchant_not_found(client, seeded):
    r = await client.post("/api/v1/merchants/merch_nope/settle")
    assert r.status_code == 404


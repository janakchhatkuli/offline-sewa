"""API endpoint tests — Block 3A."""
from decimal import Decimal

import pytest

from app.services import qr_service


# --- QR encode/decode unit tests --------------------------------------------
def test_qr_roundtrip_signature_valid():
    body = {
        "customer_id": "cust_x",
        "amount": "10.00",
        "nonce": "abc123",
        "issued_at": 1_700_000_000,
        "expires_at": 1_700_000_300,
    }
    payload = qr_service._encode_payload(body)
    decoded = qr_service._decode_payload(payload)
    assert decoded == body


def test_qr_tampered_body_rejected():
    body = {
        "customer_id": "cust_x",
        "amount": "10.00",
        "nonce": "abc123",
        "issued_at": 1_700_000_000,
        "expires_at": 1_700_000_300,
    }
    payload = qr_service._encode_payload(body)
    version, body_b64, sig = payload.split(".")
    # flip one char in body
    tampered_body = body_b64[:-1] + ("A" if body_b64[-1] != "A" else "B")
    tampered = f"{version}.{tampered_body}.{sig}"
    with pytest.raises(qr_service.InvalidSignature):
        qr_service._decode_payload(tampered)


def test_qr_malformed_structure():
    with pytest.raises(qr_service.MalformedQR):
        qr_service._decode_payload("not-a-valid-qr")


# --- Create endpoint --------------------------------------------------------
@pytest.mark.asyncio
async def test_create_offline_qr_success(client, seeded):
    r = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "100.50"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["customer_id"] == "cust_test01"
    assert data["qr_payload"].startswith("v1.")
    assert Decimal(data["amount"]) == Decimal("100.50")


@pytest.mark.asyncio
async def test_create_offline_qr_customer_missing(client, seeded):
    r = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_nope", "amount": "10.00"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_create_offline_qr_insufficient_balance(client, seeded):
    r = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "9999.00"},
    )
    assert r.status_code == 409
    assert r.json()["detail"]["error"] == "insufficient_balance"


@pytest.mark.asyncio
async def test_create_offline_qr_invalid_amount(client, seeded):
    r = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "0"},
    )
    assert r.status_code == 422


# --- Verify endpoint --------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_offline_qr_success(client, seeded):
    create = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "50.00"},
    )
    payload = create.json()["qr_payload"]

    r = await client.post(
        "/api/v1/transactions/verify-offline-qr",
        json={"merchant_id": "merch_test01", "qr_payload": payload},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "pending_settlement"
    assert data["customer_id"] == "cust_test01"
    assert data["merchant_id"] == "merch_test01"
    assert Decimal(data["amount"]) == Decimal("50.00")


@pytest.mark.asyncio
async def test_verify_offline_qr_replay_rejected(client, seeded):
    create = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "25.00"},
    )
    payload = create.json()["qr_payload"]

    r1 = await client.post(
        "/api/v1/transactions/verify-offline-qr",
        json={"merchant_id": "merch_test01", "qr_payload": payload},
    )
    assert r1.status_code == 200

    r2 = await client.post(
        "/api/v1/transactions/verify-offline-qr",
        json={"merchant_id": "merch_test01", "qr_payload": payload},
    )
    assert r2.status_code == 409
    assert r2.json()["detail"]["error"] == "nonce_already_used"


@pytest.mark.asyncio
async def test_verify_offline_qr_invalid_signature(client, seeded):
    create = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "10.00"},
    )
    payload = create.json()["qr_payload"]
    version, body, sig = payload.split(".")
    tampered_sig = sig[:-1] + ("A" if sig[-1] != "A" else "B")
    tampered = f"{version}.{body}.{tampered_sig}"

    r = await client.post(
        "/api/v1/transactions/verify-offline-qr",
        json={"merchant_id": "merch_test01", "qr_payload": tampered},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_verify_offline_qr_merchant_missing(client, seeded):
    create = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "10.00"},
    )
    payload = create.json()["qr_payload"]
    r = await client.post(
        "/api/v1/transactions/verify-offline-qr",
        json={"merchant_id": "merch_nope", "qr_payload": payload},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_verify_offline_qr_expired(client, seeded, monkeypatch):
    create = await client.post(
        "/api/v1/transactions/create-offline-qr",
        json={"customer_id": "cust_test01", "amount": "10.00"},
    )
    payload = create.json()["qr_payload"]

    # Fast-forward time inside the service module
    import app.services.qr_service as qr_mod
    real_datetime = qr_mod.datetime

    class _FakeDT(real_datetime):
        @classmethod
        def now(cls, tz=None):
            base = real_datetime.now(tz)
            return base.replace(year=base.year + 1)

    monkeypatch.setattr(qr_mod, "datetime", _FakeDT)

    r = await client.post(
        "/api/v1/transactions/verify-offline-qr",
        json={"merchant_id": "merch_test01", "qr_payload": payload},
    )
    assert r.status_code == 410


# --- Customer/Merchant GET --------------------------------------------------
@pytest.mark.asyncio
async def test_get_customer(client, seeded):
    r = await client.get("/api/v1/customers/cust_test01")
    assert r.status_code == 200
    assert r.json()["customer_id"] == "cust_test01"


@pytest.mark.asyncio
async def test_get_merchant(client, seeded):
    r = await client.get("/api/v1/merchants/merch_test01")
    assert r.status_code == 200
    assert r.json()["merchant_id"] == "merch_test01"


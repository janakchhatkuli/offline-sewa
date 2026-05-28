# API Reference

Auto-generated docs available at `/docs` (Swagger) and `/redoc` once the backend is running.
This file holds curated examples; keep in sync with the OpenAPI spec.

Base URL: `http://localhost:8000/api/v1`

---

## Block 3A — Core endpoints

### POST `/transactions/create-offline-qr`

Issues a signed, time-bound QR payload that a customer can display offline.
No balance is deducted here; deduction happens on verification.

Request:
```json
{ "customer_id": "cust_test01", "amount": "100.50" }
```

Response `200`:
```json
{
  "qr_payload": "v1.eyJhbW91bnQiOiIxMDAuNTAi...,
  "nonce": "f3b1...",
  "customer_id": "cust_test01",
  "amount": "100.50",
  "issued_at": "2026-05-28T10:00:00Z",
  "expires_at": "2026-05-28T10:05:00Z"
}
```

Errors: `404 not_found` · `403 inactive_account` · `409 insufficient_balance` · `422 invalid_amount`.

QR payload format: `v1.<base64url(json_body)>.<base64url(hmac_sha256)>`
where body keys are `customer_id`, `amount`, `nonce`, `issued_at`, `expires_at`.
Signature uses HMAC-SHA256 with `SECRET_KEY`.

### POST `/transactions/verify-offline-qr`

Verifies a QR payload, debits the customer, credits the merchant's
`pending_settlement`, and writes one `offline_transactions` row + one
`nonce_log` row atomically.

Request:
```json
{ "merchant_id": "merch_test01", "qr_payload": "v1.<body>.<sig>" }
```

Response `200`:
```json
{
  "transaction_id": "TXN1A2B3C4D",
  "status": "pending_settlement",
  "customer_id": "cust_test01",
  "merchant_id": "merch_test01",
  "amount": "100.50",
  "nonce": "f3b1...",
  "created_at": "2026-05-28T10:01:12Z"
}
```

Errors: `400 malformed_qr` · `401 invalid_signature` · `404 not_found` ·
`403 inactive_account` · `409 nonce_already_used` · `409 insufficient_balance` ·
`410 expired_qr` · `422 invalid_amount`.

### GET `/customers/{customer_id}`
Returns the customer record. `404 not_found` if absent.

### GET `/merchants/{merchant_id}`
Returns the merchant record. `404 not_found` if absent.

### Error envelope

All Block 3A errors use FastAPI's standard envelope with a structured detail:
```json
{ "detail": { "error": "insufficient_balance", "detail": "offline balance is insufficient" } }
```

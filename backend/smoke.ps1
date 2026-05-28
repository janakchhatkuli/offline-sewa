$base = "http://127.0.0.1:8000/api/v1"
Write-Host "=== GET customer ==="
Invoke-RestMethod "$base/customers/cust_demo" | ConvertTo-Json
Write-Host "=== GET merchant ==="
Invoke-RestMethod "$base/merchants/merch_demo" | ConvertTo-Json
Write-Host "=== Create QR ==="
$qr = Invoke-RestMethod -Method POST "$base/transactions/create-offline-qr" -ContentType 'application/json' -Body '{"customer_id":"cust_demo","amount":"120.50"}'
$qr | ConvertTo-Json
Write-Host "=== Verify QR ==="
$body = @{ merchant_id = "merch_demo"; qr_payload = $qr.qr_payload } | ConvertTo-Json
Invoke-RestMethod -Method POST "$base/transactions/verify-offline-qr" -ContentType 'application/json' -Body $body | ConvertTo-Json
Write-Host "=== Replay (should 409) ==="
try { Invoke-RestMethod -Method POST "$base/transactions/verify-offline-qr" -ContentType 'application/json' -Body $body | ConvertTo-Json } catch { Write-Host ("status: " + $_.Exception.Response.StatusCode.value__); Write-Host $_.ErrorDetails.Message }
Write-Host "=== Balances after ==="
Invoke-RestMethod "$base/customers/cust_demo" | ConvertTo-Json
Invoke-RestMethod "$base/merchants/merch_demo" | ConvertTo-Json

/// Result returned by `verify-offline-qr` and the customer history endpoint.
class OfflineTransaction {
  OfflineTransaction({
    required this.transactionId,
    required this.customerId,
    required this.merchantId,
    required this.amount,
    required this.nonce,
    required this.status,
    required this.createdAt,
  });

  final String transactionId;
  final String customerId;
  final String merchantId;
  final double amount;
  final String nonce;
  final String status;
  final DateTime createdAt;

  factory OfflineTransaction.fromJson(Map<String, dynamic> json) =>
      OfflineTransaction(
        transactionId: json['transaction_id'] as String,
        customerId: json['customer_id'] as String,
        merchantId: json['merchant_id'] as String,
        amount: _toDouble(json['amount']),
        nonce: json['nonce'] as String,
        status: json['status'] as String,
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

/// Result returned by `create-offline-qr`.
class OfflineQR {
  OfflineQR({
    required this.qrPayload,
    required this.nonce,
    required this.customerId,
    required this.amount,
    required this.issuedAt,
    required this.expiresAt,
  });

  final String qrPayload;
  final String nonce;
  final String customerId;
  final double amount;
  final DateTime issuedAt;
  final DateTime expiresAt;

  factory OfflineQR.fromJson(Map<String, dynamic> json) => OfflineQR(
        qrPayload: json['qr_payload'] as String,
        nonce: json['nonce'] as String,
        customerId: json['customer_id'] as String,
        amount: _toDouble(json['amount']),
        issuedAt: DateTime.parse(json['issued_at'] as String),
        expiresAt: DateTime.parse(json['expires_at'] as String),
      );
}

double _toDouble(dynamic v) {
  if (v is num) return v.toDouble();
  if (v is String) return double.tryParse(v) ?? 0.0;
  return 0.0;
}

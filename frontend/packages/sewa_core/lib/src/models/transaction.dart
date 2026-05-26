/// Offline transaction model. Implement in Block 4/5.
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
}

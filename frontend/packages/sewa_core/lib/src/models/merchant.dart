/// Merchant model. Implement with freezed in Block 5.
class Merchant {
  Merchant({
    required this.merchantId,
    required this.name,
    required this.phone,
    required this.pendingSettlement,
    required this.settledBalance,
  });

  final String merchantId;
  final String name;
  final String phone;
  final double pendingSettlement;
  final double settledBalance;
}

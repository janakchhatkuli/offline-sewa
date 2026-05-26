/// Customer model. Implement with freezed in Block 4.
class Customer {
  Customer({
    required this.customerId,
    required this.name,
    required this.phone,
    required this.onlineBalance,
    required this.offlineBalance,
  });

  final String customerId;
  final String name;
  final String phone;
  final double onlineBalance;
  final double offlineBalance;
}

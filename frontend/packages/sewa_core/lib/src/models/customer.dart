/// Customer model returned by `/api/v1/customers/{id}` and `/auth/me`.
class Customer {
  Customer({
    required this.customerId,
    required this.name,
    required this.phone,
    this.address,
    required this.onlineBalance,
    required this.offlineBalance,
    required this.isActive,
  });

  final String customerId;
  final String name;
  final String phone;
  final String? address;
  final double onlineBalance;
  final double offlineBalance;
  final bool isActive;

  factory Customer.fromJson(Map<String, dynamic> json) => Customer(
        customerId: json['customer_id'] as String,
        name: json['name'] as String,
        phone: json['phone'] as String,
        address: json['address'] as String?,
        onlineBalance: _toDouble(json['online_balance']),
        offlineBalance: _toDouble(json['offline_balance']),
        isActive: json['is_active'] as bool? ?? true,
      );
}

double _toDouble(dynamic v) {
  if (v is num) return v.toDouble();
  if (v is String) return double.tryParse(v) ?? 0.0;
  return 0.0;
}

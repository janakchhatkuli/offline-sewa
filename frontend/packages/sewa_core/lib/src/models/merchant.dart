/// Merchant model returned by `/api/v1/merchants/{id}` and `/auth/me`.
class Merchant {
  Merchant({
    required this.merchantId,
    required this.name,
    required this.phone,
    this.businessName,
    this.businessAddress,
    this.businessPhone,
    this.businessType,
    this.panNumber,
    required this.pendingSettlement,
    required this.settledBalance,
    required this.isActive,
  });

  final String merchantId;
  final String name;
  final String phone;
  final String? businessName;
  final String? businessAddress;
  final String? businessPhone;
  final String? businessType;
  final String? panNumber;
  final double pendingSettlement;
  final double settledBalance;
  final bool isActive;

  factory Merchant.fromJson(Map<String, dynamic> json) => Merchant(
        merchantId: json['merchant_id'] as String,
        name: json['name'] as String,
        phone: json['phone'] as String,
        businessName: json['business_name'] as String?,
        businessAddress: json['business_address'] as String?,
        businessPhone: json['business_phone'] as String?,
        businessType: json['business_type'] as String?,
        panNumber: json['pan_number'] as String?,
        pendingSettlement: _toDouble(json['pending_settlement']),
        settledBalance: _toDouble(json['settled_balance']),
        isActive: json['is_active'] as bool? ?? true,
      );
}

/// Response from `POST /api/v1/merchants/{id}/settle`.
class SettleResult {
  SettleResult({
    required this.merchantId,
    required this.settledCount,
    required this.settledAmount,
    required this.pendingSettlement,
    required this.settledBalance,
  });

  final String merchantId;
  final int settledCount;
  final double settledAmount;
  final double pendingSettlement;
  final double settledBalance;

  factory SettleResult.fromJson(Map<String, dynamic> json) => SettleResult(
        merchantId: json['merchant_id'] as String,
        settledCount: (json['settled_count'] as num).toInt(),
        settledAmount: _toDouble(json['settled_amount']),
        pendingSettlement: _toDouble(json['pending_settlement']),
        settledBalance: _toDouble(json['settled_balance']),
      );
}

double _toDouble(dynamic v) {
  if (v is num) return v.toDouble();
  if (v is String) return double.tryParse(v) ?? 0.0;
  return 0.0;
}

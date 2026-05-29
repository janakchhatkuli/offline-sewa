import 'package:sewa_core/sewa_core.dart';

import 'auth_session.dart';

/// Thin façade over [ApiClient] for merchant auth + QR + settlement calls.
class MerchantRepository {
  MerchantRepository({required this.api, required this.session});

  final ApiClient api;
  final AuthSession session;

  Future<AuthResponse> registerMerchant({
    required String name,
    required String phone,
    required String password,
    required String businessName,
    required String businessAddress,
    String? businessPhone,
    String? businessType,
    String? panNumber,
  }) async {
    final data = await api.post(Endpoints.registerMerchant, body: {
      'name': name,
      'phone': phone,
      'password': password,
      'business_name': businessName,
      'business_address': businessAddress,
      if (businessPhone != null && businessPhone.isNotEmpty)
        'business_phone': businessPhone,
      if (businessType != null && businessType.isNotEmpty)
        'business_type': businessType,
      if (panNumber != null && panNumber.isNotEmpty) 'pan_number': panNumber,
    });
    final auth = AuthResponse.fromJson(Map<String, dynamic>.from(data));
    await session.save(
        token: auth.accessToken, role: auth.role, userId: auth.userId);
    return auth;
  }

  Future<AuthResponse> login({
    required String phone,
    required String password,
  }) async {
    final data = await api.post(Endpoints.login, body: {
      'phone': phone,
      'password': password,
      'role': 'merchant',
    });
    final auth = AuthResponse.fromJson(Map<String, dynamic>.from(data));
    await session.save(
        token: auth.accessToken, role: auth.role, userId: auth.userId);
    return auth;
  }

  Future<Merchant> fetchMe() async {
    final data = await api.get(Endpoints.me);
    final user = Map<String, dynamic>.from(data['user'] as Map);
    return Merchant.fromJson(user);
  }

  Future<Merchant> fetchMerchant(String id) async {
    final data = await api.get(Endpoints.merchant(id));
    return Merchant.fromJson(Map<String, dynamic>.from(data));
  }

  Future<OfflineTransaction> verifyQr({
    required String merchantId,
    required String qrPayload,
  }) async {
    final data = await api.post(Endpoints.verifyQr, body: {
      'merchant_id': merchantId,
      'qr_payload': qrPayload,
    });
    return OfflineTransaction.fromJson(Map<String, dynamic>.from(data));
  }

  Future<SettleResult> settle(String merchantId) async {
    final data = await api.post(Endpoints.settle(merchantId));
    return SettleResult.fromJson(Map<String, dynamic>.from(data));
  }
}

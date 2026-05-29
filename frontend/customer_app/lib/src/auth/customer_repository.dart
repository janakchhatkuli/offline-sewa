import 'package:sewa_core/sewa_core.dart';

import 'auth_session.dart';

/// Thin façade over [ApiClient] for auth + customer + transaction calls.
class CustomerRepository {
  CustomerRepository({required this.api, required this.session});

  final ApiClient api;
  final AuthSession session;

  Future<AuthResponse> registerCustomer({
    required String name,
    required String phone,
    required String password,
    required String address,
    required DateTime dob,
    required String gender,
  }) async {
    final data = await api.post(Endpoints.registerCustomer, body: {
      'name': name,
      'phone': phone,
      'password': password,
      'address': address,
      'dob':
          '${dob.year.toString().padLeft(4, '0')}-${dob.month.toString().padLeft(2, '0')}-${dob.day.toString().padLeft(2, '0')}',
      'gender': gender,
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
      'role': 'customer',
    });
    final auth = AuthResponse.fromJson(Map<String, dynamic>.from(data));
    await session.save(
        token: auth.accessToken, role: auth.role, userId: auth.userId);
    return auth;
  }

  Future<Customer> fetchMe() async {
    final data = await api.get(Endpoints.me);
    final user = Map<String, dynamic>.from(data['user'] as Map);
    return Customer.fromJson(user);
  }

  Future<Customer> fetchCustomer(String id) async {
    final data = await api.get(Endpoints.customer(id));
    return Customer.fromJson(Map<String, dynamic>.from(data));
  }

  Future<OfflineQR> createQR({
    required String customerId,
    required double amount,
  }) async {
    final data = await api.post(Endpoints.createQr, body: {
      'customer_id': customerId,
      'amount': amount.toStringAsFixed(2),
    });
    return OfflineQR.fromJson(Map<String, dynamic>.from(data));
  }

  Future<Customer> topUp({
    required String customerId,
    required double amount,
    String target = 'offline',
  }) async {
    final data = await api.post(Endpoints.customerTopUp(customerId), body: {
      'amount': amount.toStringAsFixed(2),
      'target': target,
    });
    return Customer.fromJson(Map<String, dynamic>.from(data));
  }

  Future<List<OfflineTransaction>> fetchHistory(String customerId) async {
    final data = await api.get(Endpoints.customerTransactions(customerId));
    final list = (data as List).cast<Map>();
    return list
        .map((m) => OfflineTransaction.fromJson(Map<String, dynamic>.from(m)))
        .toList();
  }
}

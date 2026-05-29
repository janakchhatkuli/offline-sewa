/// Centralized endpoint paths. Keep in sync with backend `api/v1`.
class Endpoints {
  static const registerCustomer = '/api/v1/auth/customer/register';
  static const registerMerchant = '/api/v1/auth/merchant/register';
  static const login = '/api/v1/auth/login';
  static const me = '/api/v1/auth/me';

  static const createQr = '/api/v1/transactions/create-offline-qr';
  static const verifyQr = '/api/v1/transactions/verify-offline-qr';

  static String customer(String id) => '/api/v1/customers/$id';
  static String customerTopUp(String id) => '/api/v1/customers/$id/topup';
  static String customerTransactions(String id) =>
      '/api/v1/customers/$id/transactions';

  static String merchant(String id) => '/api/v1/merchants/$id';
  static String settle(String id) => '/api/v1/merchants/$id/settle';

  static const smsConfirm = '/api/v1/sms/confirm-payment';
  static const adminStats = '/api/v1/admin/stats';
  static const adminTransactions = '/api/v1/admin/transactions';
}

/// Centralized endpoint paths. Keep in sync with backend `api/v1`.
class Endpoints {
  static const createQr = '/api/v1/transactions/create-offline-qr';
  static const verifyQr = '/api/v1/transactions/verify-offline-qr';
  static String customer(String id) => '/api/v1/customers/$id';
  static String merchant(String id) => '/api/v1/merchants/$id';
  static String settle(String id) => '/api/v1/merchants/$id/settle';
  static const smsConfirm = '/api/v1/sms/confirm-payment';
  static const adminStats = '/api/v1/admin/stats';
  static const adminTransactions = '/api/v1/admin/transactions';
}

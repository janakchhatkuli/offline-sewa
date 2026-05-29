/// Thrown for any non-2xx response or transport error from the backend.
class ApiException implements Exception {
  ApiException({
    required this.statusCode,
    required this.code,
    required this.message,
  });

  final int statusCode;
  final String code;
  final String message;

  factory ApiException.fromBody(int statusCode, dynamic body) {
    String code = 'unknown_error';
    String message = body?.toString() ?? 'Request failed';
    if (body is Map) {
      final detail = body['detail'];
      if (detail is Map) {
        code = (detail['error'] ?? code).toString();
        message = (detail['detail'] ?? message).toString();
      } else if (detail is String) {
        message = detail;
      } else if (body['error'] != null) {
        code = body['error'].toString();
        message = (body['detail'] ?? message).toString();
      }
    }
    return ApiException(statusCode: statusCode, code: code, message: message);
  }

  @override
  String toString() => 'ApiException($statusCode $code): $message';
}

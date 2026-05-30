import 'package:dio/dio.dart';

import 'api_exception.dart';

/// Lightweight wrapper around Dio that:
///  - injects the bearer token from [tokenProvider] into every request
///  - normalizes backend error envelopes into [ApiException]
class ApiClient {
  ApiClient({required this.baseUrl, this.tokenProvider})
      : _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 30),
          sendTimeout: const Duration(seconds: 30),
          contentType: 'application/json',
          responseType: ResponseType.json,
        )) {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        final token = tokenProvider?.call();
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
    ));
  }

  String baseUrl;
  final String? Function()? tokenProvider;
  final Dio _dio;

  /// Update the base URL used for all subsequent requests (e.g. after the
  /// user picks a different backend address from a settings screen).
  void setBaseUrl(String url) {
    baseUrl = url;
    _dio.options.baseUrl = url;
  }

  Future<dynamic> get(String path, {Map<String, dynamic>? query}) =>
      _send(() => _dio.get(path, queryParameters: query));

  Future<dynamic> post(String path, {Object? body}) =>
      _send(() => _dio.post(path, data: body));

  Future<dynamic> _send(Future<Response> Function() call) async {
    try {
      final r = await call();
      return r.data;
    } on DioException catch (e) {
      final status = e.response?.statusCode ?? 0;
      final body = e.response?.data;
      if (body != null) {
        throw ApiException.fromBody(status, body);
      }
      throw ApiException(
        statusCode: status,
        code: _codeFor(e.type),
        message: _messageFor(e, baseUrl),
      );
    }
  }

  static String _codeFor(DioExceptionType t) {
    switch (t) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return 'timeout';
      case DioExceptionType.connectionError:
        return 'connection_error';
      case DioExceptionType.badCertificate:
        return 'bad_certificate';
      case DioExceptionType.cancel:
        return 'cancelled';
      case DioExceptionType.badResponse:
        return 'bad_response';
      case DioExceptionType.unknown:
        return 'network_error';
    }
  }

  static String _messageFor(DioException e, String baseUrl) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return 'Could not reach the server at $baseUrl. '
            'Check that the backend is running and the Server URL is correct.';
      case DioExceptionType.connectionError:
        return 'No connection to $baseUrl. '
            'Check Wi-Fi and the Server URL (Settings).';
      default:
        return e.message ?? 'Request failed';
    }
  }
}

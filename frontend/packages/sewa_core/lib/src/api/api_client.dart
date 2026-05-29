import 'package:dio/dio.dart';

import 'api_exception.dart';

/// Lightweight wrapper around Dio that:
///  - injects the bearer token from [tokenProvider] into every request
///  - normalizes backend error envelopes into [ApiException]
class ApiClient {
  ApiClient({required this.baseUrl, this.tokenProvider})
      : _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 15),
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

  final String baseUrl;
  final String? Function()? tokenProvider;
  final Dio _dio;

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
      throw ApiException.fromBody(status, body ?? e.message);
    }
  }
}

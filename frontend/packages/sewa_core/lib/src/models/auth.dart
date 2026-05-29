/// Token + role returned by auth endpoints.
class AuthResponse {
  AuthResponse({
    required this.accessToken,
    required this.role,
    required this.userId,
  });

  final String accessToken;
  final String role;
  final String userId;

  factory AuthResponse.fromJson(Map<String, dynamic> json) => AuthResponse(
        accessToken: json['access_token'] as String,
        role: json['role'] as String,
        userId: json['user_id'] as String,
      );
}

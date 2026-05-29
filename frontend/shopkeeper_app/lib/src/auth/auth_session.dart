import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Persisted auth state for the shopkeeper app.
class AuthSession extends ChangeNotifier {
  AuthSession._(this._prefs);

  static const _kToken = 'auth_token';
  static const _kRole = 'auth_role';
  static const _kUserId = 'auth_user_id';

  final SharedPreferences _prefs;

  static Future<AuthSession> load() async {
    final prefs = await SharedPreferences.getInstance();
    return AuthSession._(prefs);
  }

  String? get token => _prefs.getString(_kToken);
  String? get role => _prefs.getString(_kRole);
  String? get userId => _prefs.getString(_kUserId);
  bool get isAuthenticated =>
      (token?.isNotEmpty ?? false) && (userId?.isNotEmpty ?? false);

  Future<void> save({
    required String token,
    required String role,
    required String userId,
  }) async {
    await _prefs.setString(_kToken, token);
    await _prefs.setString(_kRole, role);
    await _prefs.setString(_kUserId, userId);
    notifyListeners();
  }

  Future<void> clear() async {
    await _prefs.remove(_kToken);
    await _prefs.remove(_kRole);
    await _prefs.remove(_kUserId);
    notifyListeners();
  }
}

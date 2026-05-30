import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Build-time + runtime configuration. The base URL is resolved as:
///  1. Runtime override saved in [SharedPreferences] (see [setApiBaseUrl]).
///  2. Compile-time `--dart-define=API_BASE_URL=...`.
///  3. Platform default (emulator loopback on Android, localhost elsewhere).
class AppConfig {
  static const _override = String.fromEnvironment('API_BASE_URL');
  static const _smsShortcode =
      String.fromEnvironment('SMS_SHORTCODE', defaultValue: '34001');
  static const _kApiBaseUrl = 'cfg_api_base_url';

  static String? _runtimeOverride;

  /// Must be called once during app startup before [apiBaseUrl] is read.
  static Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString(_kApiBaseUrl);
    if (stored != null && stored.isNotEmpty) {
      _runtimeOverride = stored;
    }
  }

  static Future<void> setApiBaseUrl(String url) async {
    final trimmed = url.trim();
    final prefs = await SharedPreferences.getInstance();
    if (trimmed.isEmpty) {
      _runtimeOverride = null;
      await prefs.remove(_kApiBaseUrl);
    } else {
      _runtimeOverride = trimmed;
      await prefs.setString(_kApiBaseUrl, trimmed);
    }
  }

  static String get defaultApiBaseUrl {
    if (_override.isNotEmpty) return _override;
    if (kIsWeb) return 'http://localhost:8000';
    // 10.0.2.2 is the Android *emulator* loopback to the host.
    // Physical devices must override via the Server URL screen or
    // --dart-define=API_BASE_URL=http://<host-lan-ip>:8000
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    return 'http://localhost:8000';
  }

  static String get apiBaseUrl => _runtimeOverride ?? defaultApiBaseUrl;

  /// Sparrow SMS shortcode the merchant phone texts when offline.
  /// Override with `--dart-define=SMS_SHORTCODE=12345`.
  static String get smsShortcode => _smsShortcode;
}

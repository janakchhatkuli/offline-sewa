import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';

/// Build-time configuration. Override with `--dart-define=API_BASE_URL=...`.
class AppConfig {
  static const _override = String.fromEnvironment('API_BASE_URL');
  static const _smsShortcode =
      String.fromEnvironment('SMS_SHORTCODE', defaultValue: '34001');

  static String get apiBaseUrl {
    if (_override.isNotEmpty) return _override;
    if (kIsWeb) return 'http://localhost:8000';
    // 10.0.2.2 is the Android *emulator* loopback to the host.
    // Physical devices must override with --dart-define=API_BASE_URL=http://<host-lan-ip>:8000
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    return 'http://localhost:8000';
  }

  /// Sparrow SMS shortcode the merchant phone texts when offline.
  /// Override with `--dart-define=SMS_SHORTCODE=12345`.
  static String get smsShortcode => _smsShortcode;
}

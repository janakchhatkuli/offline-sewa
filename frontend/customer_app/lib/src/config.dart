import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';

/// Build-time configuration. Override with `--dart-define=API_BASE_URL=...`.
class AppConfig {
  static const _override = String.fromEnvironment('API_BASE_URL');

  /// Picks a sensible default API base URL per platform:
  ///  - Android emulator: 10.0.2.2 (host loopback alias)
  ///  - Everything else (web, Windows/macOS/Linux desktop, iOS sim): localhost
  /// On a real phone, set --dart-define=API_BASE_URL=http://<your-pc-lan-ip>:8000
  static String get apiBaseUrl {
    if (_override.isNotEmpty) return _override;
    if (kIsWeb) return 'http://localhost:8000';
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    return 'http://localhost:8000';
  }
}

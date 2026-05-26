import 'package:flutter/material.dart';

/// Shared theme for all Sewa apps.
class SewaTheme {
  static ThemeData light() => ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF667EEA)),
        useMaterial3: true,
      );
}

import 'package:flutter/material.dart';
import 'package:sewa_core/sewa_core.dart';

import 'src/app.dart';

void main() {
  runApp(const ShopkeeperApp());
}

class ShopkeeperApp extends StatelessWidget {
  const ShopkeeperApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Offline Sewa — Shopkeeper',
      theme: SewaTheme.light(),
      home: const ShopkeeperHome(),
    );
  }
}

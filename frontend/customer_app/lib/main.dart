import 'package:flutter/material.dart';
import 'package:sewa_core/sewa_core.dart';

import 'src/app.dart';

void main() {
  runApp(const CustomerApp());
}

class CustomerApp extends StatelessWidget {
  const CustomerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Offline Sewa — Customer',
      theme: SewaTheme.light(),
      home: const CustomerHome(),
    );
  }
}

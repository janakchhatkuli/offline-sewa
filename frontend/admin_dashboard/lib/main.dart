import 'package:flutter/material.dart';
import 'package:sewa_core/sewa_core.dart';

import 'src/app.dart';

void main() {
  runApp(const AdminDashboardApp());
}

class AdminDashboardApp extends StatelessWidget {
  const AdminDashboardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Offline Sewa — Admin',
      theme: SewaTheme.light(),
      home: const DashboardHome(),
    );
  }
}

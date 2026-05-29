import 'package:flutter/material.dart';

import 'auth/auth_session.dart';
import 'auth/customer_repository.dart';
import 'features/auth/login_screen.dart';
import 'features/home/home_screen.dart';

/// Inherited scope that exposes the [AuthSession] + [CustomerRepository]
/// to the entire widget tree and rebuilds dependants when auth changes.
class SessionScope extends InheritedNotifier<AuthSession> {
  const SessionScope({
    super.key,
    required AuthSession session,
    required this.repository,
    required super.child,
  }) : super(notifier: session);

  final CustomerRepository repository;

  static SessionScope of(BuildContext context) {
    final scope =
        context.dependOnInheritedWidgetOfExactType<SessionScope>();
    assert(scope != null, 'SessionScope missing in widget tree');
    return scope!;
  }

  AuthSession get session => notifier!;
}

/// Routes to [HomeScreen] when authenticated, otherwise [LoginScreen].
class CustomerRoot extends StatelessWidget {
  const CustomerRoot({super.key});

  @override
  Widget build(BuildContext context) {
    final session = SessionScope.of(context).session;
    return session.isAuthenticated
        ? const HomeScreen()
        : const LoginScreen();
  }
}

import 'package:flutter/material.dart';
import 'package:sewa_core/sewa_core.dart';

import 'src/app.dart';
import 'src/auth/auth_session.dart';
import 'src/auth/customer_repository.dart';
import 'src/config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final session = await AuthSession.load();
  final api = ApiClient(
    baseUrl: AppConfig.apiBaseUrl,
    tokenProvider: () => session.token,
  );
  final repo = CustomerRepository(api: api, session: session);
  runApp(CustomerApp(session: session, repository: repo));
}

class CustomerApp extends StatelessWidget {
  const CustomerApp({
    super.key,
    required this.session,
    required this.repository,
  });

  final AuthSession session;
  final CustomerRepository repository;

  @override
  Widget build(BuildContext context) {
    return SessionScope(
      session: session,
      repository: repository,
      child: MaterialApp(
        title: 'Offline Sewa — Customer',
        theme: SewaTheme.light(),
        home: const CustomerRoot(),
      ),
    );
  }
}

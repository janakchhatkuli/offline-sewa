import 'package:flutter/material.dart';
import 'package:sewa_core/sewa_core.dart';

import 'src/app.dart';
import 'src/auth/auth_session.dart';
import 'src/auth/merchant_repository.dart';
import 'src/config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppConfig.load();
  final session = await AuthSession.load();
  final api = ApiClient(
    baseUrl: AppConfig.apiBaseUrl,
    tokenProvider: () => session.token,
  );
  final repo = MerchantRepository(api: api, session: session);
  runApp(ShopkeeperApp(session: session, repository: repo));
}

class ShopkeeperApp extends StatelessWidget {
  const ShopkeeperApp({
    super.key,
    required this.session,
    required this.repository,
  });

  final AuthSession session;
  final MerchantRepository repository;

  @override
  Widget build(BuildContext context) {
    return SessionScope(
      session: session,
      repository: repository,
      child: MaterialApp(
        title: 'Offline Sewa — Shopkeeper',
        theme: SewaTheme.light(),
        home: const ShopkeeperRoot(),
      ),
    );
  }
}

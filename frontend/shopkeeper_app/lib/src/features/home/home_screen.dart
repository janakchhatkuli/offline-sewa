import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:sewa_core/sewa_core.dart';

import '../../app.dart';
import '../scan/scan_screen.dart';
import '../sms/sms_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Future<Merchant>? _meFuture;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _meFuture ??= _load();
  }

  Future<Merchant> _load() => SessionScope.of(context).repository.fetchMe();

  Future<void> _refresh() async {
    setState(() => _meFuture = _load());
    await _meFuture;
  }

  Future<void> _logout() async {
    await SessionScope.of(context).session.clear();
  }

  Future<void> _settle(Merchant me) async {
    final messenger = ScaffoldMessenger.of(context);
    try {
      final result =
          await SessionScope.of(context).repository.settle(me.merchantId);
      if (!mounted) return;
      messenger.showSnackBar(SnackBar(
        content: Text(
          'Settled ${result.settledCount} txn(s) — Rs ${result.settledAmount.toStringAsFixed(2)}',
        ),
      ));
      await _refresh();
    } on ApiException catch (e) {
      if (!mounted) return;
      messenger.showSnackBar(SnackBar(content: Text('Settle failed: ${e.message}')));
    } catch (e) {
      if (!mounted) return;
      messenger.showSnackBar(SnackBar(content: Text('Settle failed: $e')));
    }
  }

  Future<void> _openScan(Merchant me) async {
    final txn = await Navigator.of(context).push<OfflineTransaction>(
      MaterialPageRoute(builder: (_) => ScanScreen(merchant: me)),
    );
    if (txn != null) await _refresh();
  }

  void _openSms(Merchant me) {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => SmsScreen(merchant: me)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final money = NumberFormat.currency(symbol: 'Rs ', decimalDigits: 2);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Shopkeeper'),
        actions: [
          IconButton(
            tooltip: 'Sign out',
            onPressed: _logout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: FutureBuilder<Merchant>(
          future: _meFuture,
          builder: (context, snap) {
            if (snap.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snap.hasError) {
              return ListView(
                children: [
                  const SizedBox(height: 80),
                  Center(child: Text('Error: ${snap.error}')),
                  const SizedBox(height: 20),
                  Center(
                    child: FilledButton.tonal(
                      onPressed: _refresh,
                      child: const Text('Retry'),
                    ),
                  ),
                ],
              );
            }
            final me = snap.data!;
            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _BalanceCard(
                  title: 'Pending settlement',
                  amount: money.format(me.pendingSettlement),
                  color: Theme.of(context).colorScheme.tertiaryContainer,
                  hint: 'Verified offline payments awaiting payout',
                ),
                const SizedBox(height: 12),
                _BalanceCard(
                  title: 'Settled balance',
                  amount: money.format(me.settledBalance),
                  color: Theme.of(context).colorScheme.primaryContainer,
                  hint: 'Lifetime total paid out',
                ),
                const SizedBox(height: 24),
                Text(me.businessName ?? me.name,
                    style: Theme.of(context).textTheme.titleMedium),
                if (me.businessAddress != null)
                  Text(me.businessAddress!,
                      style: Theme.of(context).textTheme.bodySmall),
                Text(me.merchantId,
                    style: Theme.of(context).textTheme.bodySmall),
                const SizedBox(height: 24),
                Row(
                  children: [
                    Expanded(
                      child: FilledButton.icon(
                        icon: const Icon(Icons.qr_code_scanner),
                        label: const Text('Scan QR'),
                        onPressed: () => _openScan(me),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: OutlinedButton.icon(
                        icon: const Icon(Icons.sms_outlined),
                        label: const Text('SMS fallback'),
                        onPressed: () => _openSms(me),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                FilledButton.tonalIcon(
                  icon: const Icon(Icons.account_balance),
                  label: const Text('Settle pending'),
                  onPressed:
                      me.pendingSettlement > 0 ? () => _settle(me) : null,
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _BalanceCard extends StatelessWidget {
  const _BalanceCard({
    required this.title,
    required this.amount,
    required this.color,
    required this.hint,
  });

  final String title;
  final String amount;
  final Color color;
  final String hint;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: color,
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 8),
            Text(amount,
                style: Theme.of(context)
                    .textTheme
                    .headlineMedium
                    ?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(hint, style: Theme.of(context).textTheme.bodySmall),
          ],
        ),
      ),
    );
  }
}

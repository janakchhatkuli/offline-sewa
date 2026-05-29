import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:sewa_core/sewa_core.dart';

import '../../app.dart';
import '../history/history_screen.dart';
import '../qr/qr_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Future<Customer>? _meFuture;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _meFuture ??= _load();
  }

  Future<Customer> _load() => SessionScope.of(context).repository.fetchMe();

  Future<void> _refresh() async {
    setState(() => _meFuture = _load());
    await _meFuture;
  }

  Future<void> _logout() async {
    await SessionScope.of(context).session.clear();
  }

  Future<void> _topUp(Customer me) async {
    final result = await showDialog<_TopUpResult>(
      context: context,
      builder: (_) => const _TopUpDialog(),
    );
    if (result == null || !mounted) return;
    final messenger = ScaffoldMessenger.of(context);
    try {
      await SessionScope.of(context).repository.topUp(
            customerId: me.customerId,
            amount: result.amount,
            target: result.target,
          );
      if (!mounted) return;
      messenger.showSnackBar(
        SnackBar(content: Text('Top-up of Rs ${result.amount.toStringAsFixed(2)} successful')),
      );
      await _refresh();
    } catch (e) {
      if (!mounted) return;
      messenger.showSnackBar(SnackBar(content: Text('Top-up failed: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final money = NumberFormat.currency(symbol: 'Rs ', decimalDigits: 2);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Offline Sewa'),
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
        child: FutureBuilder<Customer>(
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
                  title: 'Offline balance',
                  amount: money.format(me.offlineBalance),
                  color: Theme.of(context).colorScheme.primaryContainer,
                  hint: 'Available to spend without internet',
                ),
                const SizedBox(height: 12),
                _BalanceCard(
                  title: 'Online balance',
                  amount: money.format(me.onlineBalance),
                  color: Theme.of(context).colorScheme.secondaryContainer,
                  hint: 'Top up moves into offline balance',
                ),
                const SizedBox(height: 24),
                Text('Hi, ${me.name}',
                    style: Theme.of(context).textTheme.titleMedium),
                Text(me.customerId,
                    style: Theme.of(context).textTheme.bodySmall),
                const SizedBox(height: 24),
                Row(
                  children: [
                    Expanded(
                      child: FilledButton.icon(
                        icon: const Icon(Icons.qr_code_2),
                        label: const Text('Generate QR'),
                        onPressed: () => Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => QrScreen(customer: me),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: OutlinedButton.icon(
                        icon: const Icon(Icons.history),
                        label: const Text('History'),
                        onPressed: () => Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) =>
                                HistoryScreen(customerId: me.customerId),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                FilledButton.tonalIcon(
                  icon: const Icon(Icons.account_balance_wallet),
                  label: const Text('Top up balance'),
                  onPressed: () => _topUp(me),
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

class _TopUpResult {
  const _TopUpResult(this.amount, this.target);
  final double amount;
  final String target;
}

class _TopUpDialog extends StatefulWidget {
  const _TopUpDialog();

  @override
  State<_TopUpDialog> createState() => _TopUpDialogState();
}

class _TopUpDialogState extends State<_TopUpDialog> {
  final _formKey = GlobalKey<FormState>();
  final _amountCtrl = TextEditingController();
  String _target = 'offline';

  @override
  void dispose() {
    _amountCtrl.dispose();
    super.dispose();
  }

  void _submit() {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    final amount = double.parse(_amountCtrl.text.trim());
    Navigator.of(context).pop(_TopUpResult(amount, _target));
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Top up balance'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: _amountCtrl,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              autofocus: true,
              decoration: const InputDecoration(
                labelText: 'Amount (Rs)',
                prefixIcon: Icon(Icons.currency_rupee),
              ),
              validator: (v) {
                final n = double.tryParse((v ?? '').trim());
                if (n == null || n <= 0) return 'Enter an amount greater than 0';
                return null;
              },
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _target,
              decoration: const InputDecoration(labelText: 'Destination'),
              items: const [
                DropdownMenuItem(value: 'offline', child: Text('Offline balance')),
                DropdownMenuItem(value: 'online', child: Text('Online balance')),
              ],
              onChanged: (v) => setState(() => _target = v ?? 'offline'),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(onPressed: _submit, child: const Text('Top up')),
      ],
    );
  }
}

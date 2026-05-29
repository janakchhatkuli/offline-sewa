import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:sewa_core/sewa_core.dart';

import '../../app.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key, required this.customerId});

  final String customerId;

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  late Future<List<OfflineTransaction>> _future;

  @override
  void initState() {
    super.initState();
    _future = _load();
  }

  Future<List<OfflineTransaction>> _load() =>
      SessionScope.of(context).repository.fetchHistory(widget.customerId);

  Future<void> _refresh() async {
    setState(() => _future = _load());
    await _future;
  }

  @override
  Widget build(BuildContext context) {
    final money = NumberFormat.currency(symbol: 'Rs ', decimalDigits: 2);
    final dt = DateFormat('MMM d, HH:mm');
    return Scaffold(
      appBar: AppBar(title: const Text('Transaction history')),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: FutureBuilder<List<OfflineTransaction>>(
          future: _future,
          builder: (context, snap) {
            if (snap.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snap.hasError) {
              return ListView(
                children: [
                  const SizedBox(height: 80),
                  Center(child: Text('Error: ${snap.error}')),
                ],
              );
            }
            final items = snap.data ?? const [];
            if (items.isEmpty) {
              return ListView(
                children: const [
                  SizedBox(height: 120),
                  Center(child: Text('No transactions yet')),
                ],
              );
            }
            return ListView.separated(
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemBuilder: (context, i) {
                final t = items[i];
                final settled = t.status == 'settled';
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: settled
                        ? Colors.green.shade100
                        : Colors.orange.shade100,
                    child: Icon(
                      settled ? Icons.check : Icons.hourglass_top,
                      color: settled
                          ? Colors.green.shade800
                          : Colors.orange.shade800,
                    ),
                  ),
                  title: Text(money.format(t.amount)),
                  subtitle: Text('${t.merchantId} · ${dt.format(t.createdAt.toLocal())}'),
                  trailing: Text(
                    settled ? 'settled' : 'pending',
                    style: TextStyle(
                      color: settled
                          ? Colors.green.shade800
                          : Colors.orange.shade800,
                    ),
                  ),
                );
              },
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemCount: items.length,
            );
          },
        ),
      ),
    );
  }
}

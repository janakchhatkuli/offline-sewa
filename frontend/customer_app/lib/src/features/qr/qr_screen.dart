import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:sewa_core/sewa_core.dart';

import '../../app.dart';

class QrScreen extends StatefulWidget {
  const QrScreen({super.key, required this.customer});

  final Customer customer;

  @override
  State<QrScreen> createState() => _QrScreenState();
}

class _QrScreenState extends State<QrScreen> {
  final _amount = TextEditingController();
  OfflineQR? _qr;
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _amount.dispose();
    super.dispose();
  }

  Future<void> _generate() async {
    final value = double.tryParse(_amount.text.trim());
    if (value == null || value <= 0) {
      setState(() => _error = 'Enter a valid amount');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final qr = await SessionScope.of(context).repository.createQR(
            customerId: widget.customer.customerId,
            amount: value,
          );
      setState(() => _qr = qr);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final money = NumberFormat.currency(symbol: 'Rs ', decimalDigits: 2);
    return Scaffold(
      appBar: AppBar(title: const Text('Generate offline QR')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Offline balance: ${money.format(widget.customer.offlineBalance)}',
                  style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 16),
              TextField(
                controller: _amount,
                keyboardType:
                    const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                  labelText: 'Amount',
                  prefixText: 'Rs ',
                  border: OutlineInputBorder(),
                ),
              ),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!,
                    style: const TextStyle(color: Colors.redAccent)),
              ],
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: _busy ? null : _generate,
                icon: const Icon(Icons.qr_code_2),
                label: Text(_busy ? 'Generating...' : 'Generate QR'),
              ),
              const SizedBox(height: 24),
              if (_qr != null) _QrCard(qr: _qr!),
            ],
          ),
        ),
      ),
    );
  }
}

class _QrCard extends StatelessWidget {
  const _QrCard({required this.qr});

  final OfflineQR qr;

  @override
  Widget build(BuildContext context) {
    final fmt = DateFormat('HH:mm:ss');
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            QrImageView(
              data: qr.qrPayload,
              size: 240,
              backgroundColor: Colors.white,
            ),
            const SizedBox(height: 12),
            Text('Rs ${qr.amount.toStringAsFixed(2)}',
                style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 4),
            Text(
              'Expires at ${fmt.format(qr.expiresAt.toLocal())}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () async {
                await Clipboard.setData(ClipboardData(text: qr.qrPayload));
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('QR payload copied')),
                  );
                }
              },
              icon: const Icon(Icons.copy),
              label: const Text('Copy payload'),
            ),
          ],
        ),
      ),
    );
  }
}

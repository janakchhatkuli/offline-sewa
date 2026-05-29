import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:sewa_core/sewa_core.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../config.dart';

/// Offline fallback: when the shopkeeper has no internet but can still send
/// an SMS, this screen builds a `PAY <merchant_id> <qr_payload>` body and
/// hands it to the phone's default SMS app, pre-addressed to the Sparrow
/// shortcode. The server's `/api/v1/sms/confirm-payment` webhook processes
/// the inbound message and credits the merchant.
class SmsScreen extends StatefulWidget {
  const SmsScreen({
    super.key,
    required this.merchant,
    this.initialPayload,
  });

  final Merchant merchant;

  /// Optional pre-filled QR payload (e.g. when launched from the scan screen
  /// after a network failure).
  final String? initialPayload;

  @override
  State<SmsScreen> createState() => _SmsScreenState();
}

class _SmsScreenState extends State<SmsScreen> {
  late final TextEditingController _qr =
      TextEditingController(text: widget.initialPayload ?? '');

  @override
  void dispose() {
    _qr.dispose();
    super.dispose();
  }

  String get _smsBody {
    final payload = _qr.text.trim();
    if (payload.isEmpty) return '';
    return 'PAY ${widget.merchant.merchantId} $payload';
  }

  String get _shortcode => AppConfig.smsShortcode;

  Future<void> _copy() async {
    await Clipboard.setData(ClipboardData(text: _smsBody));
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('SMS body copied')),
      );
    }
  }

  Future<void> _send() async {
    final uri = Uri(
      scheme: 'sms',
      path: _shortcode,
      queryParameters: {'body': _smsBody},
    );
    final messenger = ScaffoldMessenger.of(context);
    try {
      final ok = await launchUrl(uri, mode: LaunchMode.externalApplication);
      if (!ok && mounted) {
        messenger.showSnackBar(
          const SnackBar(content: Text('No SMS app available')),
        );
      }
    } catch (e) {
      if (mounted) {
        messenger.showSnackBar(
          SnackBar(content: Text('Could not open SMS app: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Send via SMS (offline)')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'No internet? Paste the scanned QR payload below, then tap '
                '"Send via SMS" to text it to shortcode $_shortcode. The '
                'server processes the SMS and credits your account.',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _qr,
                maxLines: 4,
                decoration: const InputDecoration(
                  labelText: 'QR payload',
                  border: OutlineInputBorder(),
                ),
                onChanged: (_) => setState(() {}),
              ),
              const SizedBox(height: 16),
              Text('SMS to send', style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: 8),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: SelectableText(
                    _smsBody.isEmpty ? '(enter a payload above)' : _smsBody,
                    style: const TextStyle(fontFamily: 'monospace'),
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Text('To: $_shortcode',
                  style: Theme.of(context).textTheme.bodySmall),
              const SizedBox(height: 16),
              FilledButton.icon(
                icon: const Icon(Icons.sms),
                label: const Text('Send via SMS'),
                onPressed: _smsBody.isEmpty ? null : _send,
              ),
              const SizedBox(height: 8),
              OutlinedButton.icon(
                icon: const Icon(Icons.copy),
                label: const Text('Copy SMS body'),
                onPressed: _smsBody.isEmpty ? null : _copy,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

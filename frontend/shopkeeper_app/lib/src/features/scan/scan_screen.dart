import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:sewa_core/sewa_core.dart';

import '../../app.dart';
import '../sms/sms_screen.dart';

/// Scans a customer's offline-QR with the camera and posts it to
/// `/verify-offline-qr`. Pops with the resulting [OfflineTransaction] on
/// success so the caller can refresh balances.
class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key, required this.merchant});

  final Merchant merchant;

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final MobileScannerController _controller = MobileScannerController(
    formats: [BarcodeFormat.qrCode],
  );
  bool _busy = false;
  String? _error;
  String? _lastPayload;
  OfflineTransaction? _result;

  Future<void> _scanFromGallery() async {
    if (_busy) return;
    final FilePickerResult? picked = await FilePicker.platform.pickFiles(
      type: FileType.image,
      allowMultiple: false,
      withData: false,
    );
    final path = picked?.files.single.path;
    if (path == null) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final BarcodeCapture? capture =
          await _controller.analyzeImage(path);
      final code = capture?.barcodes
          .map((b) => b.rawValue)
          .firstWhere((v) => v != null && v.isNotEmpty, orElse: () => null);
      if (code == null) {
        setState(() => _error = 'No QR code found in selected image');
        return;
      }
      await _verify(code);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _onDetect(BarcodeCapture capture) async {
    if (_busy || _result != null) return;
    final code = capture.barcodes
        .map((b) => b.rawValue)
        .firstWhere((v) => v != null && v.isNotEmpty, orElse: () => null);
    if (code == null) return;
    await _verify(code);
  }

  Future<void> _verify(String payload) async {
    setState(() {
      _busy = true;
      _error = null;
      _lastPayload = payload;
    });
    await _controller.stop();
    try {
      final txn = await SessionScope.of(context).repository.verifyQr(
            merchantId: widget.merchant.merchantId,
            qrPayload: payload,
          );
      setState(() => _result = txn);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
      await _controller.start();
    } catch (e) {
      setState(() => _error = e.toString());
      await _controller.start();
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan customer QR'),
        actions: [
          IconButton(
            tooltip: 'Pick image file',
            icon: const Icon(Icons.image_outlined),
            onPressed: _busy ? null : _scanFromGallery,
          ),
          IconButton(
            tooltip: 'Toggle torch',
            icon: const Icon(Icons.flash_on),
            onPressed: () => _controller.toggleTorch(),
          ),
          IconButton(
            tooltip: 'Switch camera',
            icon: const Icon(Icons.cameraswitch),
            onPressed: () => _controller.switchCamera(),
          ),
        ],
      ),
      body: _result != null
          ? _ResultView(
              txn: _result!,
              onDone: () => Navigator.of(context).pop(_result),
            )
          : Column(
              children: [
                Expanded(
                  child: MobileScanner(
                    controller: _controller,
                    onDetect: _onDetect,
                  ),
                ),
                if (_busy)
                  const Padding(
                    padding: EdgeInsets.all(12),
                    child: LinearProgressIndicator(),
                  ),
                if (_error != null)
                  Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      children: [
                        Text(_error!,
                            style: const TextStyle(color: Colors.redAccent)),
                        if (_lastPayload != null) ...[
                          const SizedBox(height: 8),
                          OutlinedButton.icon(
                            icon: const Icon(Icons.sms),
                            label: const Text('Send via SMS instead'),
                            onPressed: () => Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => SmsScreen(
                                  merchant: widget.merchant,
                                  initialPayload: _lastPayload,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    children: [
                      const Text(
                        'Point the camera at the customer\'s QR code',
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 8),
                      OutlinedButton.icon(
                        onPressed: _busy ? null : _scanFromGallery,
                        icon: const Icon(Icons.image_outlined),
                        label: const Text('Pick image from device'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }
}

class _ResultView extends StatelessWidget {
  const _ResultView({required this.txn, required this.onDone});

  final OfflineTransaction txn;
  final VoidCallback onDone;

  @override
  Widget build(BuildContext context) {
    final money = NumberFormat.currency(symbol: 'Rs ', decimalDigits: 2);
    final dt = DateFormat('MMM d, HH:mm:ss');
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 24),
          Icon(Icons.check_circle,
              size: 96, color: Colors.green.shade600),
          const SizedBox(height: 12),
          Text('Payment ${txn.status}',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 24),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(money.format(txn.amount),
                      style: Theme.of(context).textTheme.headlineMedium),
                  const SizedBox(height: 8),
                  Text('Customer: ${txn.customerId}'),
                  Text('Txn: ${txn.transactionId}'),
                  Text('At: ${dt.format(txn.createdAt.toLocal())}'),
                ],
              ),
            ),
          ),
          const Spacer(),
          FilledButton(
            onPressed: onDone,
            child: const Text('Done'),
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:sewa_core/sewa_core.dart';

import '../../config.dart';

/// Lets the merchant point the app at a different backend host (e.g. their
/// LAN IP when running on a physical device).
class ServerSettingsScreen extends StatefulWidget {
  const ServerSettingsScreen({super.key, required this.api});

  final ApiClient api;

  @override
  State<ServerSettingsScreen> createState() => _ServerSettingsScreenState();
}

class _ServerSettingsScreenState extends State<ServerSettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _url =
      TextEditingController(text: AppConfig.apiBaseUrl);
  bool _busy = false;

  @override
  void dispose() {
    _url.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _busy = true);
    final url = _url.text.trim();
    await AppConfig.setApiBaseUrl(url);
    widget.api.setBaseUrl(AppConfig.apiBaseUrl);
    if (!mounted) return;
    Navigator.of(context).pop();
  }

  Future<void> _resetDefault() async {
    setState(() => _busy = true);
    await AppConfig.setApiBaseUrl('');
    widget.api.setBaseUrl(AppConfig.apiBaseUrl);
    if (!mounted) return;
    setState(() {
      _url.text = AppConfig.apiBaseUrl;
      _busy = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Server URL')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Point the app at the Offline Sewa backend. On a physical '
                  'device, use your computer\'s LAN IP, e.g. '
                  'http://192.168.1.50:8000',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _url,
                  keyboardType: TextInputType.url,
                  autocorrect: false,
                  decoration: const InputDecoration(
                    labelText: 'Base URL',
                    hintText: 'http://host:port',
                    border: OutlineInputBorder(),
                  ),
                  validator: (v) {
                    final s = v?.trim() ?? '';
                    if (s.isEmpty) return 'Enter URL';
                    final uri = Uri.tryParse(s);
                    if (uri == null ||
                        !uri.hasScheme ||
                        (uri.scheme != 'http' && uri.scheme != 'https') ||
                        uri.host.isEmpty) {
                      return 'Enter a valid http(s) URL';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 20),
                FilledButton(
                  onPressed: _busy ? null : _save,
                  child: const Text('Save'),
                ),
                TextButton(
                  onPressed: _busy ? null : _resetDefault,
                  child: const Text('Reset to default'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

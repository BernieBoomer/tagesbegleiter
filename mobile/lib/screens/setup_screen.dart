import 'package:flutter/material.dart';
import '../api/api_client.dart';
import 'dashboard_screen.dart';

class SetupScreen extends StatefulWidget {
  const SetupScreen({super.key});

  @override
  State<SetupScreen> createState() => _SetupScreenState();
}

class _SetupScreenState extends State<SetupScreen> {
  final _controller = TextEditingController();
  final _api = ApiClient();
  bool _checking = false;
  String? _error;

  Future<void> _submit() async {
    final key = _controller.text.trim();
    if (key.isEmpty) return;

    setState(() {
      _checking = true;
      _error = null;
    });

    try {
      final valid = await _api.verifyKey(key);
      if (!valid) {
        setState(() {
          _checking = false;
          _error = 'Key wurde vom Server abgelehnt (401). Bitte prüfen.';
        });
        return;
      }
      await ApiClient.saveApiKey(key);
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const DashboardScreen()),
      );
    } catch (e) {
      setState(() {
        _checking = false;
        _error = 'Verbindung fehlgeschlagen: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 400),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Tagesbegleiter — Einrichtung',
                  style: Theme.of(context).textTheme.titleLarge,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                const Text(
                  'API-Key eingeben. Er wird nur lokal, verschlüsselt '
                  'gespeichert (Keychain/Keystore) — niemals im Code oder '
                  'in der Cloud.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.grey),
                ),
                const SizedBox(height: 24),
                TextField(
                  controller: _controller,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'X-API-Key',
                    border: OutlineInputBorder(),
                  ),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(_error!, style: const TextStyle(color: Colors.red)),
                ],
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: _checking ? null : _submit,
                  child: _checking
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Verbinden'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

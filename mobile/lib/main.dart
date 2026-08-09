import 'package:flutter/material.dart';
import 'api/api_client.dart';
import 'screens/setup_screen.dart';
import 'screens/dashboard_screen.dart';

void main() {
  runApp(const TagesbegleiterApp());
}

class TagesbegleiterApp extends StatelessWidget {
  const TagesbegleiterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Tagesbegleiter',
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.teal),
      home: const _StartupGate(),
    );
  }
}

/// Prüft beim Start, ob bereits ein API-Key sicher gespeichert ist.
/// Falls ja: direkt zum Dashboard. Falls nein: Setup-Screen zur Eingabe.
class _StartupGate extends StatelessWidget {
  const _StartupGate();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String?>(
      future: ApiClient.loadApiKey(),
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }
        final hasKey = snapshot.data != null && snapshot.data!.isNotEmpty;
        return hasKey ? const DashboardScreen() : const SetupScreen();
      },
    );
  }
}

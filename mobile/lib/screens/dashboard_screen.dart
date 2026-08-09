import 'package:flutter/material.dart';
import '../api/api_client.dart';

/// Layout nach docs/Dashboard-UI-Spec-v0_1.md:
/// Icon-Nav | Hauptbereich (Heute, Morgen vorbereiten, Besuchsnotizen) | Seitenleiste
/// (Kontakte, Mail-Prioritäten, Diese Woche/Müllkalender, Snapshot-Inbox)
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiClient _api = ApiClient();

  List<dynamic> _todos = [];
  List<dynamic> _tomorrowEvents = [];
  List<dynamic> _openVisitNotes = [];
  List<dynamic> _contacts = [];
  Map<String, dynamic>? _mailSummary;
  Map<String, dynamic>? _waste;

  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAll();
  }

  Future<void> _loadAll() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final results = await Future.wait([
        _api.getOpenTodosToday(),
        _api.getTomorrowEvents(),
        _api.getOpenVisitNotes(),
        _api.getContacts(),
      ]);
      final mail = await _api.getMailSummaryToday();
      final waste = await _api.getWasteToday();

      setState(() {
        _todos = results[0];
        _tomorrowEvents = results[1];
        _openVisitNotes = results[2];
        _contacts = results[3];
        _mailSummary = mail;
        _waste = waste;
        _loading = false;
      });
    } on ApiKeyInvalidException {
      setState(() {
        _loading = false;
        _error = 'API-Key wurde vom Server abgelehnt. Bitte neu einrichten.';
      });
    } catch (e) {
      setState(() {
        _loading = false;
        _error = 'Verbindung fehlgeschlagen: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    if (_error != null) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(_error!, style: const TextStyle(color: Colors.red)),
              const SizedBox(height: 12),
              FilledButton(onPressed: _loadAll, child: const Text('Erneut versuchen')),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _loadAll,
        child: Row(
          children: [
            _buildIconNav(),
            const VerticalDivider(width: 1),
            Expanded(child: _buildMainArea()),
            const VerticalDivider(width: 1),
            _buildSidebar(),
          ],
        ),
      ),
    );
  }

  Widget _buildIconNav() {
    return const SizedBox(
      width: 56,
      child: Column(
        children: [
          SizedBox(height: 16),
          Icon(Icons.checklist, color: Colors.teal),
          SizedBox(height: 20),
          Icon(Icons.calendar_today),
          SizedBox(height: 20),
          Icon(Icons.contacts),
          SizedBox(height: 20),
          Icon(Icons.notes),
          SizedBox(height: 20),
          Icon(Icons.photo),
        ],
      ),
    );
  }

  Widget _buildMainArea() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _sectionTitle('Heute — ${_todos.length} offen'),
        if (_todos.isEmpty) _emptyHint('Keine offenen Todos 🎉'),
        ..._todos.map((todo) => CheckboxListTile(
              value: todo['done'] as bool? ?? false,
              title: Text(todo['text'] as String? ?? ''),
              subtitle: Text(_todoSubtitle(todo)),
              onChanged: (val) async {
                await _api.markTodoDone(todo['id'] as int, val ?? false);
                _loadAll();
              },
            )),
        const SizedBox(height: 24),
        _sectionTitle('Morgen vorbereiten'),
        if (_tomorrowEvents.isEmpty) _emptyHint('Keine Termine morgen'),
        ..._tomorrowEvents.map((event) => ListTile(
              leading: const Icon(Icons.event),
              title: Text(event['title'] as String? ?? ''),
              subtitle: Text(event['location'] as String? ?? ''),
            )),
        const SizedBox(height: 24),
        _sectionTitle('Besuchsnotizen nacharbeiten'),
        if (_openVisitNotes.isEmpty) _emptyHint('Keine offenen Follow-ups'),
        ..._openVisitNotes.map((note) => Card(
              child: ListTile(
                title: Text(note['contact_name'] as String? ?? ''),
                subtitle: Text(note['topic'] as String? ?? ''),
              ),
            )),
        const SizedBox(height: 8),
        const Row(
          children: [
            Icon(Icons.lock, size: 14, color: Colors.grey),
            SizedBox(width: 4),
            Text(
              'Lokal gespeichert, kein CRM-Sync',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSidebar() {
    return SizedBox(
      width: 240,
      child: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          _sectionTitle('Kontakte', small: true),
          ..._contacts.map((c) => ListTile(
                dense: true,
                leading: CircleAvatar(
                  radius: 14,
                  child: Text(
                    _initial(c['name'] as String?),
                    style: const TextStyle(fontSize: 12),
                  ),
                ),
                title: Text(c['name'] as String? ?? '', style: const TextStyle(fontSize: 13)),
                trailing: Icon(
                  c['channel'] == 'whatsapp' ? Icons.chat : Icons.send,
                  size: 16,
                ),
              )),
          const SizedBox(height: 20),
          _sectionTitle('Mail-Prioritäten', small: true),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Text(
              _mailSummary?['summary_text'] as String? ?? 'Keine Zusammenfassung heute',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ),
          const SizedBox(height: 20),
          _sectionTitle('Diese Woche', small: true),
          if (_waste != null) ...[
            _wasteLine('Heute', _waste!['today'] as List<dynamic>? ?? []),
            _wasteLine('Morgen', _waste!['tomorrow'] as List<dynamic>? ?? []),
          ],
          const SizedBox(height: 20),
          _sectionTitle('Snapshot-Inbox', small: true),
          const Text('0 unverarbeitet', style: TextStyle(fontSize: 12, color: Colors.grey)),
        ],
      ),
    );
  }

  Widget _wasteLine(String label, List<dynamic> categories) {
    if (categories.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Text('$label: ${categories.join(", ")}', style: const TextStyle(fontSize: 12)),
    );
  }

  String _todoSubtitle(dynamic todo) {
    final category = todo['category'] as String? ?? '';
    final source = todo['source'] as String? ?? '';
    final wiedervorlage = todo['is_wiedervorlage'] as bool? ?? false;
    if (wiedervorlage) return 'Wiedervorlage · $category';
    return '$category · $source';
  }

  String _initial(String? name) {
    if (name == null || name.isEmpty) return '?';
    return name[0].toUpperCase();
  }

  Widget _sectionTitle(String text, {bool small = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        text,
        style: TextStyle(
          fontSize: small ? 13 : 16,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _emptyHint(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Text(text, style: const TextStyle(color: Colors.grey, fontSize: 13)),
    );
  }
}

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Zentraler API-Client. Basis-URL und Auth-Header entsprechen dem
/// live verifizierten Stand vom 08.08.2026 (main.py, Commit e41b5fe):
/// Auth läuft ausschliesslich über den Header "X-API-Key", fail-closed.
///
/// WICHTIG: Der Key wird NIEMALS im Code oder in .env-Dateien im Repo
/// abgelegt (das Repo ist öffentlich!). Er wird einmalig vom Nutzer im
/// Setup-Screen eingegeben und lokal verschlüsselt gespeichert
/// (flutter_secure_storage nutzt Android Keystore / iOS Keychain /
/// Windows Credential Locker je nach Plattform).
class ApiClient {
  static const String baseUrl = 'https://tagesbegleiter.app';
  static const _storage = FlutterSecureStorage();
  static const _keyStorageKey = 'tagesbegleiter_api_key';

  String? _apiKey;

  static Future<void> saveApiKey(String key) async {
    await _storage.write(key: _keyStorageKey, value: key);
  }

  static Future<String?> loadApiKey() async {
    return _storage.read(key: _keyStorageKey);
  }

  static Future<void> clearApiKey() async {
    await _storage.delete(key: _keyStorageKey);
  }

  Future<Map<String, String>> _headers() async {
    _apiKey ??= await loadApiKey();
    if (_apiKey == null || _apiKey!.isEmpty) {
      throw ApiKeyMissingException();
    }
    return {
      'X-API-Key': _apiKey!,
      'Content-Type': 'application/json',
    };
  }

  Future<bool> verifyKey(String key) async {
    final response = await http.get(
      Uri.parse('$baseUrl/v1/todos'),
      headers: {'X-API-Key': key},
    );
    return response.statusCode == 200;
  }

  Future<List<dynamic>> getOpenTodosToday() async {
    final response = await http.get(
      Uri.parse('$baseUrl/v1/todos?status=open&date_filter=today'),
      headers: await _headers(),
    );
    _checkAuth(response);
    return jsonDecode(response.body) as List<dynamic>;
  }

  Future<void> markTodoDone(int id, bool done) async {
    final response = await http.patch(
      Uri.parse('$baseUrl/v1/todos/$id'),
      headers: await _headers(),
      body: jsonEncode({'done': done}),
    );
    _checkAuth(response);
  }

  Future<List<dynamic>> getTomorrowEvents() async {
    final response = await http.get(
      Uri.parse('$baseUrl/v1/calendar?date_filter=tomorrow'),
      headers: await _headers(),
    );
    _checkAuth(response);
    return jsonDecode(response.body) as List<dynamic>;
  }

  Future<List<dynamic>> getOpenVisitNotes() async {
    final response = await http.get(
      Uri.parse('$baseUrl/v1/visit-notes?followup=open'),
      headers: await _headers(),
    );
    _checkAuth(response);
    return jsonDecode(response.body) as List<dynamic>;
  }

  Future<List<dynamic>> getContacts() async {
    final response = await http.get(
      Uri.parse('$baseUrl/v1/contacts'),
      headers: await _headers(),
    );
    _checkAuth(response);
    return jsonDecode(response.body) as List<dynamic>;
  }

  Future<Map<String, dynamic>?> getMailSummaryToday() async {
    final response = await http.get(
      Uri.parse('$baseUrl/v1/mail/summary'),
      headers: await _headers(),
    );
    _checkAuth(response);
    if (response.body == 'null' || response.body.isEmpty) return null;
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getWasteToday() async {
    final response = await http.get(
      Uri.parse('$baseUrl/v1/waste/today'),
      headers: await _headers(),
    );
    _checkAuth(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  void _checkAuth(http.Response response) {
    if (response.statusCode == 401) {
      throw ApiKeyInvalidException();
    }
    if (response.statusCode == 500) {
      throw ApiServerException(response.body);
    }
  }
}

class ApiKeyMissingException implements Exception {}

class ApiKeyInvalidException implements Exception {}

class ApiServerException implements Exception {
  final String message;
  ApiServerException(this.message);
}

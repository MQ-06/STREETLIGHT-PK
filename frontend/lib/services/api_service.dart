// lib/services/api_service.dart
import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  
  
  // For Web (Chrome/Edge) - Use localhost
  static const String _webURL = 'http://localhost:8000';
  
  // For Android/iOS Real Device - Use laptop IP (same WiFi required)
  static const String _mobileURL = 'http://192.168.100.13:8000'; //ye mera IP ha
  
  // For Android Emulator - Use special emulator IP
  static const String _emulatorURL = 'http://10.0.2.2:8000';

  // 🚀 Smart URL Selection - Auto-detects platform
  static String get baseURL {
    if (kIsWeb) {
      // Running on Web (Chrome, Edge, etc.)
      return _webURL;
    } else {
      // Running on Mobile (Android/iOS)
      return _mobileURL;
    }
  }

  static const String _tokenKey = 'auth_token';


  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  static Future<Map<String, String>> _authHeaders() async {
    final token = await getToken();
    if (token == null) throw Exception('Not authenticated');
    return {'Authorization': 'Bearer $token'};
  }

  // ─────────────────────────────────────────────
  // AUTH (your existing methods — unchanged)
  // ─────────────────────────────────────────────

  static Future<Map<String, dynamic>> signup({
    required String firstName,
    required String lastName,
    required String email,
    required String password,
    required String cnic,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseURL/signup'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'first_name': firstName,
          'last_name': lastName,
          'cnic': cnic,
          'email': email,
          'password': password,
        }),
      ).timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'success': true, 'data': data};
      }
      return {'success': false, 'error': data['detail'] ?? 'Registration failed'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseURL/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      ).timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        await saveToken(data['access_token']);
        return {'success': true, 'data': data};
      }
      return {'success': false, 'error': data['detail'] ?? 'Login failed'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  static Future<Map<String, dynamic>> forgotPassword({
    required String email,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseURL/forget-password'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {
          'success': true,
          'message': data['message'],
          'token': data['reset_token'],
        };
      }
      return {'success': false, 'error': data['detail'] ?? 'Failed'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  static Future<Map<String, dynamic>> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseURL/reset-password'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'token': token, 'new_password': newPassword}),
      );
      final data = jsonDecode(response.body);
      return response.statusCode == 200
          ? {'success': true, 'message': data['message']}
          : {'success': false, 'error': data['detail'] ?? 'Reset failed'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  static Future<void> logout() async {
    await clearToken();
  }

  // ─────────────────────────────────────────────
  // REPORTS
  // ─────────────────────────────────────────────

  /// GET /reports/feed
  static Future<Map<String, dynamic>> getReportsFeed({
    int skip = 0,
    int limit = 20,
    String? category,
  }) async {
    try {
      final headers = await _authHeaders();
      String url = '$baseURL/reports/feed?skip=$skip&limit=$limit';
      if (category != null) url += '&category=$category';

      final response = await http
          .get(Uri.parse(url), headers: headers)
          .timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return {'success': true, 'data': data};
      } else if (response.statusCode == 401) {
        return {'success': false, 'error': 'Session expired. Please log in again.', 'code': 401};
      }
      return {'success': false, 'error': data['detail'] ?? 'Failed to load feed'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  /// POST /reports/create
  /// Image is NOT sent — only text fields. Image stays local on device.
  static Future<Map<String, dynamic>> createReport({
    required String title,
    required String description,
    required String category,
    required String locationAddress,
    String? locationCity,
    double? locationLat,
    double? locationLng,
  }) async {
    try {
      final token = await getToken();
      if (token == null) return {'success': false, 'error': 'Not authenticated.'};

      // Using multipart even without image — FastAPI Form() requires this
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseURL/reports/create'),
      );
      request.headers['Authorization'] = 'Bearer $token';
      request.fields['title'] = title;
      request.fields['description'] = description;
      request.fields['category'] = category.toUpperCase();
      request.fields['location_address'] = locationAddress;
      if (locationCity != null) request.fields['location_city'] = locationCity;
      if (locationLat != null) request.fields['location_lat'] = locationLat.toString();
      if (locationLng != null) request.fields['location_lng'] = locationLng.toString();
      // No image field — image stays on device until AI processing later

      final streamed = await request.send().timeout(const Duration(seconds: 30));
      final response = await http.Response.fromStream(streamed);
      final data = jsonDecode(response.body);

      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'success': true, 'data': data};
      }
      return {'success': false, 'error': data['detail'] ?? 'Failed to submit report'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  /// POST /reports/{id}/support — toggle
  static Future<Map<String, dynamic>> toggleSupport(int reportId) async {
    try {
      final headers = await _authHeaders();
      final response = await http
          .post(Uri.parse('$baseURL/reports/$reportId/support'), headers: headers)
          .timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      return {'success': false, 'error': data['detail'] ?? 'Failed'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  /// POST /reports/{id}/verify — toggle
  static Future<Map<String, dynamic>> toggleVerify(int reportId) async {
    try {
      final headers = await _authHeaders();
      final response = await http
          .post(Uri.parse('$baseURL/reports/$reportId/verify'), headers: headers)
          .timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      return {'success': false, 'error': data['detail'] ?? 'Failed'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  static Future<Map<String, dynamic>> getMyReports() async {
    try {
      final headers = await _authHeaders();
      final response = await http
          .get(Uri.parse('$baseURL/reports/my'), headers: headers)
          .timeout(const Duration(seconds: 15));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      return {'success': false, 'error': data['detail'] ?? 'Failed'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }
}
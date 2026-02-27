// lib/services/api_service.dart
import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart' show kDebugMode, kIsWeb;
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../config/api_config.dart';

class ApiService {
  // Set to true when running on Android Emulator
  static const bool _useEmulator = false;

  /// Timeout for auth requests (login/signup). Use 25s on WiFi for slow networks.
  static const Duration _authTimeout = Duration(seconds: 25);

  static String get baseURL {
    if (kIsWeb) return ApiConfig.webUrl;
    if (_useEmulator) return ApiConfig.emulatorUrl;
    return ApiConfig.mobileUrl;
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
      ).timeout(_authTimeout);
      final data = jsonDecode(response.body);
      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'success': true, 'data': data};
      }
      return {'success': false, 'error': data['detail'] ?? 'Registration failed'};
    } catch (e) {
      if (kDebugMode) {
        print('Signup error: $e');
        print('Trying to reach: $baseURL');
      }
      final isTimeout = e is TimeoutException;
      return {
        'success': false,
        'error': isTimeout
            ? 'Connection timed out. Check that backend is running and phone/PC are on same WiFi.'
            : 'Cannot connect to server.',
      };
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
      ).timeout(_authTimeout);
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        await saveToken(data['access_token']);
        return {'success': true, 'data': data};
      }
      return {'success': false, 'error': data['detail'] ?? 'Login failed'};
    } catch (e) {
      if (kDebugMode) {
        print('Login error: $e');
        print('Trying to reach: $baseURL');
      }
      final isTimeout = e is TimeoutException;
      return {
        'success': false,
        'error': isTimeout
            ? 'Connection timed out. Check that backend is running and phone/PC are on same WiFi.'
            : 'Cannot connect to server.',
      };
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

  /// POST /reports/create (WITH AI VALIDATION)

  static Future<Map<String, dynamic>> createReport({
    required String imagePath,  // REQUIRED: Image file path for AI processing
    required String title,
    required String description,
    required String locationAddress,
    String? locationCity,
    double? locationLat,
    double? locationLng,
  }) async {
    try {
      final token = await getToken();
      if (token == null) return {'success': false, 'error': 'Not authenticated.'};

      // Create multipart request with image
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseURL/reports/create'),
      );
      
      request.headers['Authorization'] = 'Bearer $token';
      
      // Add image file (REQUIRED for AI processing)
      request.files.add(await http.MultipartFile.fromPath('image', imagePath));
      
      // Add form fields (category is auto-detected by AI)
      request.fields['title'] = title;
      request.fields['description'] = description;
      request.fields['location_address'] = locationAddress;
      if (locationCity != null) request.fields['location_city'] = locationCity;
      if (locationLat != null) request.fields['location_lat'] = locationLat.toString();
      if (locationLng != null) request.fields['location_lng'] = locationLng.toString();

      // Longer timeout for AI processing (60 seconds)
      final streamed = await request.send().timeout(const Duration(seconds: 60));
      final response = await http.Response.fromStream(streamed);
      final data = jsonDecode(response.body);

      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'success': true, 'data': data};
      }
      
      // Handle AI validation errors (400)
      if (response.statusCode == 400) {
        // Check if detailed error structure from AI Agent
        if (data['detail'] is Map) {
          return {
            'success': false,
            'error': data['detail']['message'] ?? 'Validation failed',
            'errors': data['detail']['errors'] ?? [],
            'validation_failed': true,
            'agent_reason': data['detail']['agent_reason']
          };
        } else if (data['detail'] is String) {
          return {'success': false, 'error': data['detail']};
        }
      }
      
      return {'success': false, 'error': data['detail'] ?? 'Failed to submit report'};
      
    } on TimeoutException {
      return {'success': false, 'error': 'Request timed out. AI processing may be slow, please try again.'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server: $e'};
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
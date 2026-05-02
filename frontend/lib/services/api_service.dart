// lib/services/api_service.dart
import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart' show kDebugMode, kIsWeb;
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'user_session.dart';

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

  /// Build full URL for images (backend returns relative paths like "reports/2026/02/27/uuid.jpg")
  static String imageUrl(String path) {
    final p0 = path.trim();
    if (p0.isEmpty) return '';
    if (p0.startsWith('http://') || p0.startsWith('https://')) return p0;
    // If backend accidentally includes spaces/newlines around cloudinary URLs,
    // trim+detect before falling back to local `/uploads`.
    if (p0.contains('cloudinary.com/')) return p0;
    final p = p0.startsWith('/') ? p0 : '/uploads/$p0';
    return '$baseURL$p';
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
  // PUSH (Phase 2)
  // ─────────────────────────────────────────────

  static Future<Map<String, dynamic>> updateFcmToken(String token) async {
    try {
      final headers = await _authHeaders();
      headers['Content-Type'] = 'application/json';
      final response = await http
          .post(
            Uri.parse('$baseURL/reports/fcm-token'),
            headers: headers,
            body: jsonEncode({'fcm_token': token}),
          )
          .timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      return {'success': false, 'error': data['detail'] ?? 'Failed'};
    } catch (e) {
      if (kDebugMode) print('updateFcmToken error [${e.runtimeType}]: $e');
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  // ─────────────────────────────────────────────
  // NOTIFICATIONS (Phase 1: in-app)
  // ─────────────────────────────────────────────

  static Future<Map<String, dynamic>> getNotifications({
    bool unreadOnly = false,
    int limit = 50,
    int? cursor,
  }) async {
    try {
      final headers = await _authHeaders();
      final qp = <String, String>{
        'unread_only': unreadOnly ? 'true' : 'false',
        'limit': limit.toString(),
      };
      if (cursor != null) qp['cursor'] = cursor.toString();
      final uri = Uri.parse('$baseURL/notifications').replace(queryParameters: qp);

      final response = await http
          .get(uri, headers: headers)
          .timeout(const Duration(seconds: 15));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      return {'success': false, 'error': data['detail'] ?? 'Failed to load notifications'};
    } catch (e) {
      if (kDebugMode) print('getNotifications error [${e.runtimeType}]: $e');
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  static Future<Map<String, dynamic>> getUnreadNotificationCount() async {
    try {
      final headers = await _authHeaders();
      final response = await http
          .get(Uri.parse('$baseURL/notifications/unread-count'), headers: headers)
          .timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      return {'success': false, 'error': data['detail'] ?? 'Failed'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  static Future<Map<String, dynamic>> markNotificationRead(
    int notificationId, {
    bool read = true,
  }) async {
    try {
      final headers = await _authHeaders();
      headers['Content-Type'] = 'application/json';
      final response = await http
          .post(
            Uri.parse('$baseURL/notifications/$notificationId/read'),
            headers: headers,
            body: jsonEncode({'read': read}),
          )
          .timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      return {'success': false, 'error': data['detail'] ?? 'Failed'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
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
    await UserSession.logout();
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
          .timeout(const Duration(seconds: 30));

      final body = response.body;
      final contentType = response.headers['content-type'] ?? '';

      dynamic data;
      try {
        data = jsonDecode(body);
      } on FormatException {
        data = null;
      }

      if (response.statusCode == 200) {
        if (data is Map<String, dynamic>) {
          return {'success': true, 'data': data};
        }
        return {
          'success': false,
          'error': 'Invalid server response (expected JSON).',
        };
      }

      if (response.statusCode == 401) {
        return {'success': false, 'error': 'Session expired. Please log in again.', 'code': 401};
      }

      if (data is Map && data['detail'] != null) {
        return {'success': false, 'error': data['detail'].toString(), 'code': response.statusCode};
      }

      final preview = body.trim().isEmpty
          ? '(empty body)'
          : (body.trim().length > 200 ? '${body.trim().substring(0, 200)}…' : body.trim());
      return {
        'success': false,
        'error': 'Server error ${response.statusCode} (${contentType.isEmpty ? 'unknown content-type' : contentType}): $preview',
        'code': response.statusCode,
      };
    } on TimeoutException {
      return {'success': false, 'error': 'Request timed out (>${30}s). Server may be busy.'};
    } catch (e) {
      if (kDebugMode) print('getReportsFeed error [${e.runtimeType}]: $e');
      return {'success': false, 'error': 'Feed error [${e.runtimeType}]: $e'};
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
          final d = data['detail'] as Map<String, dynamic>;
          return {
            'success': false,
            'error': d['message'] ?? 'Validation failed',
            'errors': d['errors'] ?? [],
            'validation_failed': true,
            'agent_reason': d['agent_reason'],
            'error_code': d['error_code'],
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

  /// POST /reports/{id}/confirm-resolution — citizen confirms or rejects fix
  static Future<Map<String, dynamic>> confirmReportResolution({
    required int reportId,
    required bool confirmed,
  }) async {
    try {
      final headers = await _authHeaders();
      headers['Content-Type'] = 'application/json';
      final response = await http
          .post(
            Uri.parse('$baseURL/reports/$reportId/confirm-resolution'),
            headers: headers,
            body: jsonEncode({'confirmed': confirmed}),
          )
          .timeout(const Duration(seconds: 30));
      final raw = jsonDecode(response.body);
      if (response.statusCode == 200) {
        if (raw is Map && raw['success'] == true) {
          return {'success': true, 'data': raw};
        }
        final err = raw is Map ? raw['error']?.toString() : null;
        return {'success': false, 'error': err ?? 'Request failed'};
      }
      final detail = raw is Map ? raw['detail'] : null;
      final msg = detail is String
          ? detail
          : (detail != null ? detail.toString() : 'Failed');
      return {'success': false, 'error': msg};
    } catch (e) {
      if (kDebugMode) print('confirmReportResolution error: $e');
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  static Future<Map<String, dynamic>> getUserProfile() async {
    try {
      final headers = await _authHeaders();
      final response = await http
          .get(Uri.parse('$baseURL/users/me/profile'), headers: headers)
          .timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      return {'success': false, 'error': data['detail'] ?? 'Failed to load profile'};
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

  // ─────────────────────────────────────────────
  // COMMENTS
  // ─────────────────────────────────────────────

  /// GET /reports/{reportId}/comments
  static Future<Map<String, dynamic>> getReportComments(
    int reportId, {
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final headers = await _authHeaders();
      final response = await http
          .get(
            Uri.parse('$baseURL/reports/$reportId/comments?skip=$skip&limit=$limit'),
            headers: headers,
          )
          .timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      return {'success': false, 'error': data['detail'] ?? 'Failed to load comments'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  /// POST /reports/{reportId}/comments
  static Future<Map<String, dynamic>> createComment(
    int reportId,
    String text,
  ) async {
    try {
      final headers = await _authHeaders();
      headers['Content-Type'] = 'application/json';
      final response = await http
          .post(
            Uri.parse('$baseURL/reports/$reportId/comments'),
            headers: headers,
            body: jsonEncode({'text': text}),
          )
          .timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      return {'success': false, 'error': data['detail'] ?? 'Failed to post comment'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  /// DELETE /reports/comments/{commentId}
  static Future<Map<String, dynamic>> deleteComment(int commentId) async {
    try {
      final headers = await _authHeaders();
      final response = await http
          .delete(
            Uri.parse('$baseURL/reports/comments/$commentId'),
            headers: headers,
          )
          .timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true};
      return {'success': false, 'error': data['detail'] ?? 'Failed to delete comment'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  // ─────────────────────────────────────────────
  // COMMUNITY VERIFICATION
  // ─────────────────────────────────────────────

  /// GET /verification/pending?lat=&lng=
  static Future<Map<String, dynamic>> getPendingVerifications(
    double lat,
    double lng,
  ) async {
    try {
      final headers = await _authHeaders();
      final response = await http
          .get(
            Uri.parse('$baseURL/verification/pending?lat=$lat&lng=$lng'),
            headers: headers,
          )
          .timeout(const Duration(seconds: 15));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      if (response.statusCode == 401) {
        return {'success': false, 'error': 'Session expired. Please log in again.', 'code': 401};
      }
      return {'success': false, 'error': data['detail'] ?? 'Failed to load verifications'};
    } catch (e) {
      if (kDebugMode) print('getPendingVerifications error [${e.runtimeType}]: $e');
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  /// POST /verification/{requestId}/vote
  static Future<Map<String, dynamic>> submitVerificationVote(
    int requestId,
    String vote,
    double? lat,
    double? lng,
  ) async {
    try {
      final headers = await _authHeaders();
      headers['Content-Type'] = 'application/json';
      final response = await http
          .post(
            Uri.parse('$baseURL/verification/$requestId/vote'),
            headers: headers,
            body: jsonEncode({'vote': vote, 'lat': lat, 'lng': lng}),
          )
          .timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      return {'success': false, 'error': data['detail'] ?? 'Vote failed'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }

  /// GET /verification/{reportId}/status
  static Future<Map<String, dynamic>> getVerificationStatus(int reportId) async {
    try {
      final headers = await _authHeaders();
      final response = await http
          .get(
            Uri.parse('$baseURL/verification/$reportId/status'),
            headers: headers,
          )
          .timeout(const Duration(seconds: 10));
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) return {'success': true, 'data': data};
      if (response.statusCode == 404) {
        return {'success': false, 'error': 'No verification found', 'code': 404};
      }
      return {'success': false, 'error': data['detail'] ?? 'Failed to load status'};
    } catch (e) {
      return {'success': false, 'error': 'Cannot connect to server.'};
    }
  }
}
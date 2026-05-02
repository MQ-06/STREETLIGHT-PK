import 'package:firebase_messaging/firebase_messaging.dart';
import 'api_service.dart';

class PushNotifications {
  static final FirebaseMessaging _messaging = FirebaseMessaging.instance;

  static Future<void> init({
    required Future<void> Function(String route, Map<String, dynamic> data) onNavigate,
  }) async {
    await _messaging.requestPermission();

    final token = await _messaging.getToken();
    if (token != null && token.trim().isNotEmpty) {
      await _tryUploadToken(token);
    }

    FirebaseMessaging.instance.onTokenRefresh.listen((newToken) async {
      if (newToken.trim().isNotEmpty) {
        await _tryUploadToken(newToken);
      }
    });

    // Handle taps on notifications (app in background/terminated)
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) async {
      final data = Map<String, dynamic>.from(message.data);
      final route = (data['route'] ?? '/notifications').toString();
      await onNavigate(route, data);
    });

    final initial = await FirebaseMessaging.instance.getInitialMessage();
    if (initial != null) {
      final data = Map<String, dynamic>.from(initial.data);
      final route = (data['route'] ?? '/notifications').toString();
      await onNavigate(route, data);
    }
  }

  static Future<void> _tryUploadToken(String token) async {
    try {
      // Only works after login (bearer token stored)
      await ApiService.updateFcmToken(token);
    } catch (_) {
      // ignore: user may not be logged in yet
    }
  }

  /// Call after login/sign-in succeeds so the backend stores [fcm_token] (cold start often runs before auth).
  static Future<void> syncTokenAfterAuth() async {
    try {
      final token = await _messaging.getToken();
      if (token != null && token.trim().isNotEmpty) {
        await _tryUploadToken(token);
      }
    } catch (_) {}
  }
}


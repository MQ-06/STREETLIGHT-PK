/// API server configuration.
///
/// **Profile / release APK:** uses [productionUrl] (Render). Override at build time:
/// `flutter build apk --dart-define=API_BASE_URL=https://your-app.onrender.com`
///
/// **Debug on physical device:** [serverIp] + [serverPort] (same WiFi as PC).
///
/// **Emulator:** [emulatorUrl] when [ApiService] `_useEmulator` is true.
class ApiConfig {
  /// Deployed backend (HTTPS). Update if your Render URL changes.
  static String get productionUrl {
    const fromEnv = String.fromEnvironment('API_BASE_URL', defaultValue: '');
    if (fromEnv.isNotEmpty) {
      return fromEnv.replaceAll(RegExp(r'/+$'), '');
    }
    return 'https://streetlight-pk.onrender.com';
  }

  /// Your computer's IP on the local network. Update this when your IP changes.
  /// Run `ipconfig` to find your WiFi adapter's IPv4 (e.g. 192.168.1.7).
  static const String serverIp = '10.65.110.43';
  static const int serverPort = 8000;

  static String get mobileUrl => 'http://$serverIp:$serverPort';
  static const String emulatorUrl = 'http://10.0.2.2:8000';
  static const String webUrl = 'http://localhost:8000';
}

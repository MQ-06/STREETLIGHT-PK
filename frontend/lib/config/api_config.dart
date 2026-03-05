/// API server configuration.
///
/// For physical device: Use your computer's IP (run `ipconfig` in terminal,
/// find "IPv4 Address" under your WiFi adapter - e.g. 192.168.1.105).
/// Phone and computer must be on the same WiFi.
///
/// For emulator: Uses 10.0.2.2 (Android emulator's alias for host machine).
class ApiConfig {
  /// Your computer's IP on the local network. Update this when your IP changes.
  /// Run `ipconfig` to find your WiFi adapter's IPv4 (e.g. 192.168.1.7).
  static const String serverIp = '192.168.1.109';
  static const int serverPort = 8000;

  static String get mobileUrl => 'http://$serverIp:$serverPort';
  static const String emulatorUrl = 'http://10.0.2.2:8000';
  static const String webUrl = 'http://localhost:8000';
}

//services/user_session.dart
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

/// Simple user session management without database
/// Stores user data locally using SharedPreferences
class UserSession {
  static const String _keyIsLoggedIn = 'is_logged_in';
  static const String _keyUserName = 'user_name';
  static const String _keyUserEmail = 'user_email';
  static const String _keyUserLocation = 'user_location';
  static const String _keyProfileImage = 'profile_image_path';
  static const String _keyTotalReported = 'total_reported';
  static const String _keyTotalResolved = 'total_resolved';
  static const String _keyRegisteredUsers = 'registered_users';
  
  // ============ REGISTRATION & LOGIN VALIDATION ============
  
  /// Register a new user (stores credentials locally)
  /// Returns true if successful, false if email already exists
  static Future<bool> registerUser({
    required String firstName,
    required String lastName,
    required String email,
    required String password,
    String? cnic,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    
    // Get existing registered users
    final usersJson = prefs.getString(_keyRegisteredUsers);
    Map<String, dynamic> users = {};
    if (usersJson != null) {
      users = jsonDecode(usersJson) as Map<String, dynamic>;
    }
    
    // Check if email already registered
    final normalizedEmail = email.toLowerCase().trim();
    if (users.containsKey(normalizedEmail)) {
      return false; // User already exists
    }
    
    // Store new user
    users[normalizedEmail] = {
      'firstName': firstName,
      'lastName': lastName,
      'email': normalizedEmail,
      'password': password, // In production, this should be hashed
      'cnic': cnic,
      'registeredAt': DateTime.now().toIso8601String(),
    };
    
    await prefs.setString(_keyRegisteredUsers, jsonEncode(users));
    return true;
  }
  
  /// Validate login credentials against registered users
  /// Returns a Map with 'success' (bool) and optionally 'userData' or 'error'
  static Future<Map<String, dynamic>> validateLogin({
    required String email,
    required String password,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    
    // Get registered users
    final usersJson = prefs.getString(_keyRegisteredUsers);
    if (usersJson == null) {
      return {
        'success': false,
        'error': 'No registered users found. Please register first.',
      };
    }
    
    final users = jsonDecode(usersJson) as Map<String, dynamic>;
    final normalizedEmail = email.toLowerCase().trim();
    
    // Check if email exists
    if (!users.containsKey(normalizedEmail)) {
      return {
        'success': false,
        'error': 'Email not registered. Please register first.',
      };
    }
    
    final userData = users[normalizedEmail] as Map<String, dynamic>;
    
    // Verify password
    if (userData['password'] != password) {
      return {
        'success': false,
        'error': 'Incorrect password. Please try again.',
      };
    }
    
    return {
      'success': true,
      'userData': userData,
    };
  }
  
  /// Check if an email is already registered
  static Future<bool> isEmailRegistered(String email) async {
    final prefs = await SharedPreferences.getInstance();
    final usersJson = prefs.getString(_keyRegisteredUsers);
    if (usersJson == null) return false;
    
    final users = jsonDecode(usersJson) as Map<String, dynamic>;
    return users.containsKey(email.toLowerCase().trim());
  }
  
  // ============ SESSION MANAGEMENT ============
  
  /// Check if user is logged in
  static Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_keyIsLoggedIn) ?? false;
  }
  
  /// Login user (called after successful registration/login)
  static Future<void> login({
    required String name,
    required String email,
    String? location,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyIsLoggedIn, true);
    await prefs.setString(_keyUserName, name);
    await prefs.setString(_keyUserEmail, email);
    if (location != null) {
      await prefs.setString(_keyUserLocation, location);
    }
    // Initialize report counts
    if (!prefs.containsKey(_keyTotalReported)) {
      await prefs.setInt(_keyTotalReported, 0);
    }
    if (!prefs.containsKey(_keyTotalResolved)) {
      await prefs.setInt(_keyTotalResolved, 0);
    }
  }
  
  /// Logout user
  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyIsLoggedIn, false);
  }
  
  // ============ USER DATA GETTERS & SETTERS ============
  
  /// Get user name
  static Future<String> getUserName() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyUserName) ?? 'Guest User';
  }
  
  /// Set user name
  static Future<void> setUserName(String name) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyUserName, name);
  }
  
  /// Get user email
  static Future<String?> getUserEmail() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyUserEmail);
  }
  
  /// Get user location
  static Future<String> getUserLocation() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyUserLocation) ?? 'Location not set';
  }
  
  /// Set user location
  static Future<void> setUserLocation(String location) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyUserLocation, location);
  }
  
  /// Get profile image path
  static Future<String?> getProfileImagePath() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyProfileImage);
  }
  
  /// Set profile image path
  static Future<void> setProfileImagePath(String path) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyProfileImage, path);
  }
  
  // ============ REPORT STATISTICS ============
  
  /// Get total reported issues count
  static Future<int> getTotalReported() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_keyTotalReported) ?? 0;
  }
  
  /// Increment total reported issues count
  static Future<void> incrementTotalReported() async {
    final prefs = await SharedPreferences.getInstance();
    final current = prefs.getInt(_keyTotalReported) ?? 0;
    await prefs.setInt(_keyTotalReported, current + 1);
  }
  
  /// Get total resolved issues count
  static Future<int> getTotalResolved() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_keyTotalResolved) ?? 0;
  }
  
  /// Increment total resolved issues count
  static Future<void> incrementTotalResolved() async {
    final prefs = await SharedPreferences.getInstance();
    final current = prefs.getInt(_keyTotalResolved) ?? 0;
    await prefs.setInt(_keyTotalResolved, current + 1);
  }
  
  /// Calculate impact score (resolved / reported * 1000)
  static Future<int> calculateImpactScore() async {
    final reported = await getTotalReported();
    final resolved = await getTotalResolved();
    if (reported == 0) return 0;
    return ((resolved / reported) * 1000).toInt().clamp(0, 1000);
  }
  
  /// Calculate impact percentage
  static Future<double> calculateImpactPercentage() async {
    final reported = await getTotalReported();
    final resolved = await getTotalResolved();
    if (reported == 0) return 0.0;
    return (resolved / reported) * 100;
  }
  
  /// Clear all user data (keeps registered users)
  static Future<void> clearAllData() async {
    final prefs = await SharedPreferences.getInstance();
    // Preserve registered users when clearing data
    final registeredUsers = prefs.getString(_keyRegisteredUsers);
    await prefs.clear();
    if (registeredUsers != null) {
      await prefs.setString(_keyRegisteredUsers, registeredUsers);
    }
  }
  
  /// Clear everything including registered users (for dev/testing)
  static Future<void> clearAllIncludingUsers() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}

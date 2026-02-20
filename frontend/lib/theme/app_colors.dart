import 'package:flutter/material.dart';

/// App color palette for Streetlight app
class AppColors {
  AppColors._();

  // ===== Splash Screen Colors =====
  // Background
  static const Color background = Color(0xFF000000);

  // Light glow colors (warm white/amber)
  static const Color lightGlowStart = Color(0xFFFFFFCC);
  static const Color lightGlowEnd = Color(0xFFFFE4B5);
  static const Color lightGlowCenter = Color(0xFFFFF8DC);

  // Lamp/Post metallic colors (splash)
  static const Color lampDark = Color(0xFF555555);
  static const Color lampLight = Color(0xFF777777);
  static const Color lampHighlight = Color(0xFF999999);

  // Text
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textGlow = Color(0xFFFFE4B5);

  // Loading spinner
  static const Color spinnerColor = Color(0xFF444444);

  // Particle colors
  static const Color particleColor = Color(0xFFFFFFCC);

  // ===== Landing/Auth Screen Colors =====
  // Background browns
  static const Color darkBrown = Color(0xFF1A0F0A);
  static const Color warmBrown = Color(0xFF2D1810);

  // Gold accents
  static const Color goldPrimary = Color(0xFFD4AF37);
  static const Color goldSecondary = Color(0xFFE8C547);
  static const Color goldText = Color(0xFFB8A89F);
  static const Color glowGold = Color(0xFFFFCC66);
  static const Color borderGold = Color(0xFF8B7355);

  // Button colors
  static const Color buttonOrange = Color(0xFFFF9940);
  static const Color buttonOrangeDark = Color(0xFFFF7722);
}

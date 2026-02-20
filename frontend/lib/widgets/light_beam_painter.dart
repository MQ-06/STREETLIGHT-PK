import 'package:flutter/material.dart';

/// Custom painter for the cone-shaped light beam
class LightBeamPainter extends CustomPainter {
  final double intensity;

  LightBeamPainter({required this.intensity});

  @override
  void paint(Canvas canvas, Size size) {
    if (intensity <= 0) return;

    // Light source at center, below top
    final lampCenterX = size.width * 0.5;
    final lampCenterY = size.height * 0.12 + 15;

    // Light beam cone - wider and more vibrant yellow
    final beamPath = Path();
    beamPath.moveTo(lampCenterX - 30, lampCenterY + 10);
    beamPath.lineTo(lampCenterX - 160, size.height * 0.85);
    beamPath.lineTo(lampCenterX + 160, size.height * 0.85);
    beamPath.lineTo(lampCenterX + 30, lampCenterY + 10);
    beamPath.close();

    // Vibrant yellow gradient for the beam
    final beamPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          const Color(0xFFFFDD00).withAlpha((140 * intensity).toInt()), // Bright yellow
          const Color(0xFFFFCC00).withAlpha((80 * intensity).toInt()),
          const Color(0xFFFFAA00).withAlpha((30 * intensity).toInt()),
          Colors.transparent,
        ],
        stops: const [0.0, 0.3, 0.6, 1.0],
      ).createShader(Rect.fromLTWH(0, lampCenterY, size.width, size.height * 0.75));

    canvas.drawPath(beamPath, beamPaint);

    // Add soft edge blur effect with multiple layers
    for (int i = 1; i <= 3; i++) {
      final blurPath = Path();
      final offset = i * 12.0;
      blurPath.moveTo(lampCenterX - 30 - offset / 2, lampCenterY + 10);
      blurPath.lineTo(lampCenterX - 160 - offset, size.height * 0.85);
      blurPath.lineTo(lampCenterX + 160 + offset, size.height * 0.85);
      blurPath.lineTo(lampCenterX + 30 + offset / 2, lampCenterY + 10);
      blurPath.close();

      final blurPaint = Paint()
        ..shader = LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            const Color(0xFFFFDD00).withAlpha((30 * intensity / i).toInt()),
            const Color(0xFFFFCC00).withAlpha((15 * intensity / i).toInt()),
            Colors.transparent,
          ],
        ).createShader(Rect.fromLTWH(0, lampCenterY, size.width, size.height * 0.75));

      canvas.drawPath(blurPath, blurPaint);
    }
  }

  @override
  bool shouldRepaint(LightBeamPainter oldDelegate) {
    return oldDelegate.intensity != intensity;
  }
}

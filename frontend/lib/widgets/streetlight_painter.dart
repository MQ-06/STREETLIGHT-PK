import 'package:flutter/material.dart';


/// Custom painter for the streetlight post and lamp fixture
class StreetlightPainter extends CustomPainter {
  final double lightIntensity;

  StreetlightPainter({required this.lightIntensity});

  @override
  void paint(Canvas canvas, Size size) {
    // Position on the left side of the page
    final postX = size.width * 0.12;
    final baseY = size.height * 0.85;
    // Light comes a bit below the top
    final topY = size.height * 0.12;

    // Draw the post (black color)
    _drawPost(canvas, postX, baseY, topY);

    // Draw the arm extending to the right
    _drawArm(canvas, postX, topY, size);

    // Draw the lamp fixture
    _drawLampFixture(canvas, postX, topY, size);

    // Draw lamp glow if light is on
    if (lightIntensity > 0) {
      _drawLampGlow(canvas, postX, topY, size);
      _drawLensFlare(canvas, postX, topY, size);
    }
  }

  void _drawPost(Canvas canvas, double postX, double baseY, double topY) {
    final postWidth = 8.0;

    // Post in black/dark gray
    final postPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.centerLeft,
        end: Alignment.centerRight,
        colors: [
          const Color(0xFF1A1A1A),
          const Color(0xFF333333),
          const Color(0xFF444444),
          const Color(0xFF333333),
          const Color(0xFF1A1A1A),
        ],
        stops: const [0.0, 0.3, 0.5, 0.7, 1.0],
      ).createShader(Rect.fromLTWH(postX - postWidth / 2, topY, postWidth, baseY - topY));

    // Draw post rectangle
    final postRect = RRect.fromRectAndRadius(
      Rect.fromLTWH(postX - postWidth / 2, topY + 30, postWidth, baseY - topY - 30),
      const Radius.circular(2),
    );
    canvas.drawRRect(postRect, postPaint);

    // Post base
    final basePaint = Paint()..color = const Color(0xFF1A1A1A);
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(postX - 12, baseY - 15, 24, 15),
        const Radius.circular(2),
      ),
      basePaint,
    );
  }

  void _drawArm(Canvas canvas, double postX, double topY, Size size) {
    final armPaint = Paint()
      ..color = const Color(0xFF333333)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 6
      ..strokeCap = StrokeCap.round;

    final path = Path();
    path.moveTo(postX, topY + 30);

    // Curved arm extending to the right toward center
    final armEndX = size.width * 0.5; // End at center
    final armEndY = topY;

    path.quadraticBezierTo(
      postX + 30,
      topY - 20,
      armEndX,
      armEndY,
    );

    canvas.drawPath(path, armPaint);

    // Draw connector at base of arm
    final connectorPaint = Paint()..color = const Color(0xFF444444);
    canvas.drawCircle(Offset(postX, topY + 30), 8, connectorPaint);
  }

  void _drawLampFixture(Canvas canvas, double postX, double topY, Size size) {
    // Lamp is at center of screen
    final lampCenterX = size.width * 0.5;
    final lampCenterY = topY;

    // Lamp housing (elliptical shape) - darker
    final lampPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          const Color(0xFF555555),
          const Color(0xFF444444),
          const Color(0xFF333333),
        ],
      ).createShader(Rect.fromCenter(
        center: Offset(lampCenterX, lampCenterY),
        width: 60,
        height: 25,
      ));

    // Draw lamp body
    canvas.save();
    canvas.translate(lampCenterX, lampCenterY);

    final lampPath = Path();
    lampPath.addOval(Rect.fromCenter(
      center: Offset.zero,
      width: 55,
      height: 22,
    ));
    canvas.drawPath(lampPath, lampPaint);

    // Lamp rim
    final rimPaint = Paint()
      ..color = const Color(0xFF666666)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    canvas.drawPath(lampPath, rimPaint);

    canvas.restore();
  }

  void _drawLampGlow(Canvas canvas, double postX, double topY, Size size) {
    final lampCenterX = size.width * 0.5;
    final lampCenterY = topY + 5;

    // Vibrant yellow glow
    final innerGlowPaint = Paint()
      ..shader = RadialGradient(
        colors: [
          const Color(0xFFFFDD00).withAlpha((255 * lightIntensity).toInt()), // Bright yellow
          const Color(0xFFFFCC00).withAlpha((200 * lightIntensity).toInt()),
          const Color(0xFFFFAA00).withAlpha((120 * lightIntensity).toInt()),
          Colors.transparent,
        ],
        stops: const [0.0, 0.3, 0.6, 1.0],
      ).createShader(Rect.fromCircle(center: Offset(lampCenterX, lampCenterY), radius: 50));

    canvas.drawCircle(Offset(lampCenterX, lampCenterY), 50, innerGlowPaint);
  }

  void _drawLensFlare(Canvas canvas, double postX, double topY, Size size) {
    final lampCenterX = size.width * 0.5;
    final lampCenterY = topY + 5;

    // Horizontal lens flare line - more vibrant yellow
    final flarePaint = Paint()
      ..shader = LinearGradient(
        colors: [
          Colors.transparent,
          const Color(0xFFFFDD00).withAlpha((100 * lightIntensity).toInt()),
          const Color(0xFFFFEE44).withAlpha((180 * lightIntensity).toInt()),
          const Color(0xFFFFDD00).withAlpha((100 * lightIntensity).toInt()),
          Colors.transparent,
        ],
        stops: const [0.0, 0.3, 0.5, 0.7, 1.0],
      ).createShader(Rect.fromLTWH(lampCenterX - 100, lampCenterY - 1, 200, 2));

    canvas.drawRect(
      Rect.fromLTWH(lampCenterX - 100, lampCenterY - 1, 200, 2),
      flarePaint,
    );
  }

  @override
  bool shouldRepaint(StreetlightPainter oldDelegate) {
    return oldDelegate.lightIntensity != lightIntensity;
  }
}

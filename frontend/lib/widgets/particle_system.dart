import 'package:flutter/material.dart';
import 'dart:math' as math;


/// Particle data class
class Particle {
  double x;
  double y;
  double size;
  double opacity;
  double speedY;
  double speedX;

  Particle({
    required this.x,
    required this.y,
    required this.size,
    required this.opacity,
    required this.speedY,
    required this.speedX,
  });
}

/// Widget that displays floating dust particles in the light beam
class ParticleSystem extends StatefulWidget {
  final double intensity;

  const ParticleSystem({super.key, required this.intensity});

  @override
  State<ParticleSystem> createState() => _ParticleSystemState();
}

class _ParticleSystemState extends State<ParticleSystem>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  final List<Particle> _particles = [];
  final math.Random _random = math.Random();
  static const int particleCount = 30;

  @override
  void initState() {
    super.initState();
    _initParticles();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 10),
    )..repeat();

    _controller.addListener(_updateParticles);
  }

  void _initParticles() {
    for (int i = 0; i < particleCount; i++) {
      _particles.add(_createParticle());
    }
  }

  Particle _createParticle({double? startY}) {
    return Particle(
      x: _random.nextDouble(),
      y: startY ?? _random.nextDouble(),
      size: _random.nextDouble() * 3 + 1,
      opacity: _random.nextDouble() * 0.6 + 0.2,
      speedY: _random.nextDouble() * 0.001 + 0.0005,
      speedX: (_random.nextDouble() - 0.5) * 0.0005,
    );
  }

  void _updateParticles() {
    if (!mounted) return;

    setState(() {
      for (int i = 0; i < _particles.length; i++) {
        _particles[i].y -= _particles[i].speedY;
        _particles[i].x += _particles[i].speedX;

        // Reset particle if it goes out of bounds
        if (_particles[i].y < 0) {
          _particles[i] = _createParticle(startY: 1.0);
        }
        if (_particles[i].x < 0 || _particles[i].x > 1) {
          _particles[i].x = _random.nextDouble();
        }
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.intensity <= 0) return const SizedBox.shrink();

    return CustomPaint(
      painter: ParticlePainter(
        particles: _particles,
        intensity: widget.intensity,
      ),
      size: Size.infinite,
    );
  }
}

/// Painter for the particles
class ParticlePainter extends CustomPainter {
  final List<Particle> particles;
  final double intensity;

  ParticlePainter({required this.particles, required this.intensity});

  @override
  void paint(Canvas canvas, Size size) {
    // Match light beam position - centered
    final lampCenterX = size.width * 0.5;
    final lampCenterY = size.height * 0.12 + 15;
    final beamBottom = size.height * 0.85;

    for (final particle in particles) {
      // Calculate position within the light beam cone
      final yPos = lampCenterY + particle.y * (beamBottom - lampCenterY);

      // Calculate the width of the beam at this y position
      final progress = (yPos - lampCenterY) / (beamBottom - lampCenterY);
      final beamLeftAtY = lampCenterX - 30 - (130 * progress);
      final beamRightAtY = lampCenterX + 30 + (130 * progress);
      final beamWidth = beamRightAtY - beamLeftAtY;

      final xPos = beamLeftAtY + particle.x * beamWidth;

      // Only draw if within reasonable bounds
      if (xPos > beamLeftAtY && xPos < beamRightAtY) {
        // Yellow particles to match vibrant light
        final paint = Paint()
          ..color = const Color(0xFFFFDD88).withAlpha(
            (particle.opacity * intensity * (1 - progress * 0.5) * 255).toInt(),
          );

        canvas.drawCircle(
          Offset(xPos, yPos),
          particle.size * (1 - progress * 0.3),
          paint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(ParticlePainter oldDelegate) => true;
}

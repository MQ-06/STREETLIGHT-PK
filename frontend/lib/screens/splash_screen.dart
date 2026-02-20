import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:async';
import 'dart:math' as math;
import '../theme/app_colors.dart';
import '../widgets/streetlight_painter.dart';
import '../widgets/light_beam_painter.dart';
import '../widgets/particle_system.dart';

/// Animated splash screen for the Streetlight app
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with TickerProviderStateMixin {
  // Animation controllers
  late AnimationController _flickerController;
  late AnimationController _slideController;
  late AnimationController _textController;
  late AnimationController _idleFlickerController;

  // Animations
  late Animation<double> _slideAnimation;
  late Animation<double> _textOpacityAnimation;

  // State
  double _lightIntensity = 0.0;
  bool _isFlickering = true;
  bool _showText = false;
  bool _isIdleState = false;
  final math.Random _random = math.Random();

  @override
  void initState() {
    super.initState();
    _initAnimations();
    _startAnimationSequence();
  }

  void _initAnimations() {
    // Flicker controller (for initial flicker phase)
    _flickerController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 100),
    );

    // Slide controller (streetlight slides up)
    _slideController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1800),
    );

    _slideAnimation = Tween<double>(begin: 200, end: 0).animate(
      CurvedAnimation(parent: _slideController, curve: Curves.easeOut),
    );

    // Text fade in controller
    _textController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );

    _textOpacityAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _textController, curve: Curves.easeIn),
    );

    // Idle flicker controller (subtle periodic flicker)
    _idleFlickerController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 150),
    );
  }

  Future<void> _startAnimationSequence() async {
    // Phase 1: Flicker phase (2.5 seconds with 5 flickers)
    await _performFlickers(5);

    // Phase 2: Light ignition (stabilize)
    setState(() {
      _isFlickering = false;
      _lightIntensity = 1.0;
    });

    await Future.delayed(const Duration(milliseconds: 500));

    // Phase 3: Slide up animation
    _slideController.forward();

    // Phase 4: Text appearance (starts during slide)
    await Future.delayed(const Duration(milliseconds: 800));
    setState(() => _showText = true);
    _textController.forward();

    // Wait for animations to complete
    await Future.delayed(const Duration(milliseconds: 1500));

    // Phase 5: Enter idle state
    setState(() => _isIdleState = true);
    _startIdleFlicker();

    // Navigate to landing screen after brief idle display
    await Future.delayed(const Duration(milliseconds: 1500));
    if (mounted) {
      Navigator.of(context).pushReplacementNamed('/landing');
    }
  }

  Future<void> _performFlickers(int count) async {
    for (int i = 0; i < count; i++) {
      // Random delay between flickers
      await Future.delayed(Duration(milliseconds: 200 + _random.nextInt(400)));

      // Flicker on
      setState(() => _lightIntensity = 0.8 + _random.nextDouble() * 0.2);
      await Future.delayed(Duration(milliseconds: 50 + _random.nextInt(100)));

      // Flicker off (except for last flicker)
      if (i < count - 1) {
        setState(() => _lightIntensity = 0.0);
      }
    }
  }

  void _startIdleFlicker() {
    // Periodic subtle flicker every 3-5 seconds
    Timer.periodic(Duration(seconds: 3 + _random.nextInt(3)), (timer) {
      if (!mounted || !_isIdleState) {
        timer.cancel();
        return;
      }

      // Subtle flicker
      setState(() => _lightIntensity = 0.85);
      Future.delayed(const Duration(milliseconds: 100), () {
        if (mounted) setState(() => _lightIntensity = 1.0);
      });
    });
  }

  @override
  void dispose() {
    _flickerController.dispose();
    _slideController.dispose();
    _textController.dispose();
    _idleFlickerController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: AnimatedBuilder(
        animation: _textController,
        builder: (context, child) {
          return Stack(
            children: [
              // Light beam (behind streetlight)
              CustomPaint(
                painter: LightBeamPainter(intensity: _lightIntensity),
                size: Size.infinite,
              ),

              // Particles in the light beam
              ParticleSystem(intensity: _lightIntensity),

              // Streetlight
              CustomPaint(
                painter: StreetlightPainter(lightIntensity: _lightIntensity),
                size: Size.infinite,
              ),

              // Text and loading indicator - positioned in the light beam, below center
              if (_showText)
                Positioned(
                  top: MediaQuery.of(context).size.height * 0.62,
                  left: 0,
                  right: 0,
                  child: AnimatedBuilder(
                    animation: _textController,
                    builder: (context, child) {
                      return Opacity(
                        opacity: _textOpacityAnimation.value,
                        child: Column(
                          children: [
                            // Glowing "STREETLIGHT" text
                            _buildGlowingText(),
                            const SizedBox(height: 40),
                            // Loading spinner
                            _buildLoadingSpinner(),
                          ],
                        ),
                      );
                    },
                  ),
                ),

              // Star decoration (bottom right)
              Positioned(
                bottom: 30,
                right: 30,
                child: _buildStarDecoration(),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildGlowingText() {
    return Stack(
      children: [
        // Glow effect layer 1
        Text(
          'STREETLIGHT',
          style: GoogleFonts.outfit(
            fontSize: 32,
            fontWeight: FontWeight.w800,
            color: AppColors.textGlow.withOpacity(0.3),
            letterSpacing: 4,
          ),
        ),
        // Glow effect layer 2
        Positioned(
          child: Text(
            'STREETLIGHT',
            style: GoogleFonts.outfit(
              fontSize: 32,
              fontWeight: FontWeight.w800,
              foreground: Paint()
                ..color = AppColors.textGlow
                ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 10),
              letterSpacing: 4,
            ),
          ),
        ),
        // Main text
        Text(
          'STREETLIGHT',
          style: GoogleFonts.outfit(
            fontSize: 32,
            fontWeight: FontWeight.w800,
            color: AppColors.textPrimary,
            letterSpacing: 4,
          ),
        ),
      ],
    );
  }

  Widget _buildLoadingSpinner() {
    return SizedBox(
      width: 24,
      height: 24,
      child: CircularProgressIndicator(
        strokeWidth: 2,
        valueColor: AlwaysStoppedAnimation<Color>(
          AppColors.spinnerColor.withOpacity(0.8),
        ),
      ),
    );
  }

  Widget _buildStarDecoration() {
    return Icon(
      Icons.star_rounded,
      color: AppColors.lampLight.withOpacity(0.6),
      size: 28,
    );
  }
}

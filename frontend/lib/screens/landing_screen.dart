import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_colors.dart';

/// Landing screen that appears after splash - shows streetlight hero and login/register buttons
class LandingScreen extends StatefulWidget {
  const LandingScreen({super.key});

  @override
  State<LandingScreen> createState() => _LandingScreenState();
}

class _LandingScreenState extends State<LandingScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();

    // Configure status bar for dark theme
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        systemNavigationBarColor: AppColors.darkBrown,
        systemNavigationBarIconBrightness: Brightness.light,
      ),
    );

    // Fade-in animation
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeIn),
    );

    // Start fade-in
    _fadeController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;
    final screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      body: AnimatedBuilder(
        animation: _fadeController,
        builder: (context, child) {
          return Opacity(
            opacity: _fadeAnimation.value,
            child: Container(
              width: double.infinity,
              height: double.infinity,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    AppColors.darkBrown,
                    AppColors.warmBrown,
                  ],
                ),
              ),
              child: SafeArea(
                child: Column(
                  children: [
                    // Streetlight illustration
                    Expanded(
                      flex: 5,
                      child: _buildStreetlightIllustration(screenHeight, screenWidth),
                    ),

                    // Text section
                    _buildTextSection(),

                    const SizedBox(height: 30),

                    // Buttons section
                    Expanded(
                      flex: 3,
                      child: _buildButtonsSection(context),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildStreetlightIllustration(double screenHeight, double screenWidth) {
    return SizedBox(
      width: double.infinity,
      child: CustomPaint(
        painter: LandingStreetlightPainter(),
        size: Size(screenWidth, screenHeight * 0.45),
      ),
    );
  }

  Widget _buildTextSection() {
    return Column(
      children: [
        // STREETLIGHT title
        Text(
          'STREETLIGHT',
          style: GoogleFonts.outfit(
            fontSize: 36,
            fontWeight: FontWeight.w800,
            color: AppColors.goldPrimary,
            letterSpacing: 6.0,
          ),
        ),
        const SizedBox(height: 8),
        // Decorative line
        Container(
          width: 60,
          height: 1,
          color: AppColors.goldPrimary.withAlpha(128),
        ),
        const SizedBox(height: 12),
        // Subtitle
        Text(
          '"no civic hazard should remain in the dark"',
          textAlign: TextAlign.center,
          style: GoogleFonts.inter(
            fontSize: 14,
            fontWeight: FontWeight.w400,
            fontStyle: FontStyle.italic,
            color: AppColors.goldText,
            letterSpacing: 1.0,
          ),
        ),
      ],
    );
  }

  Widget _buildButtonsSection(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          const SizedBox(height: 20),
          // LOGIN button
          _buildLoginButton(context),
          const SizedBox(height: 14),
          // REGISTER button
          _buildRegisterButton(context),
          const Spacer(),
          // Footer
          _buildFooter(),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildLoginButton(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          Navigator.of(context).pushNamed('/login_form');
        },
        borderRadius: BorderRadius.circular(20),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 18),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [AppColors.buttonOrange, AppColors.buttonOrangeDark],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: AppColors.buttonOrange.withAlpha(77),
                blurRadius: 15,
                offset: const Offset(0, 5),
              ),
            ],
          ),
          child: Center(
            child: Text(
              'LOGIN',
              style: GoogleFonts.inter(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Colors.white,
                letterSpacing: 2.0,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRegisterButton(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          Navigator.of(context).pushNamed('/register_form');
        },
        borderRadius: BorderRadius.circular(20),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 18),
          decoration: BoxDecoration(
            color: Colors.transparent,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: AppColors.borderGold,
              width: 1.5,
            ),
          ),
          child: Center(
            child: Text(
              'REGISTER',
              style: GoogleFonts.inter(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: AppColors.goldPrimary,
                letterSpacing: 2.0,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFooter() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Page indicators
        Row(
          children: [
            _buildDot(true),
            const SizedBox(width: 8),
            _buildDot(false),
            const SizedBox(width: 8),
            _buildDot(false),
          ],
        ),
      ],
    );
  }

  Widget _buildDot(bool isActive) {
    return Container(
      width: 8,
      height: 8,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: isActive
            ? AppColors.goldText.withAlpha(204)
            : AppColors.goldText.withAlpha(77),
      ),
    );
  }
}

/// Custom painter for the streetlight illustration on landing screen
class LandingStreetlightPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final centerX = size.width / 2;
    final lampY = size.height * 0.05;
    final poleBottom = size.height * 0.95;

    // Draw light beam first (behind everything)
    _drawLightBeam(canvas, size, centerX, lampY);

    // Draw the pole
    _drawPole(canvas, centerX, lampY, poleBottom);

    // Draw the lamp fixture
    _drawLampFixture(canvas, centerX, lampY);
  }

  void _drawLightBeam(Canvas canvas, Size size, double centerX, double lampY) {
    final beamPath = Path();
    final lampWidth = 90.0;
    final beamBottom = size.height * 0.85;

    beamPath.moveTo(centerX - lampWidth / 2, lampY + 25);
    beamPath.lineTo(centerX - lampWidth * 1.5, beamBottom);
    beamPath.lineTo(centerX + lampWidth * 1.5, beamBottom);
    beamPath.lineTo(centerX + lampWidth / 2, lampY + 25);
    beamPath.close();

    // Gradient for the beam
    final beamPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          AppColors.glowGold.withAlpha(102),
          AppColors.glowGold.withAlpha(51),
          AppColors.glowGold.withAlpha(13),
          Colors.transparent,
        ],
        stops: const [0.0, 0.3, 0.6, 1.0],
      ).createShader(Rect.fromLTWH(0, lampY, size.width, beamBottom - lampY));

    canvas.drawPath(beamPath, beamPaint);
  }

  void _drawPole(Canvas canvas, double centerX, double lampY, double poleBottom) {
    final poleWidth = 6.0;

    // Main pole
    final polePaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.centerLeft,
        end: Alignment.centerRight,
        colors: [
          AppColors.warmBrown,
          const Color(0xFF4A3528),
          const Color(0xFF3D2A1F),
        ],
      ).createShader(Rect.fromLTWH(centerX - poleWidth / 2, lampY + 20, poleWidth, poleBottom - lampY - 20));

    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(centerX - poleWidth / 2, lampY + 20, poleWidth, poleBottom - lampY - 20),
        const Radius.circular(2),
      ),
      polePaint,
    );

    // Highlight stripe on pole
    final highlightPaint = Paint()
      ..color = const Color(0xFF5A4538).withAlpha(128);
    canvas.drawRect(
      Rect.fromLTWH(centerX - 1, lampY + 20, 2, poleBottom - lampY - 20),
      highlightPaint,
    );

    // Orange indicator dot
    final dotY = poleBottom * 0.55;
    final dotPaint = Paint()..color = AppColors.buttonOrange;
    canvas.drawCircle(Offset(centerX, dotY), 4, dotPaint);

    // Dot glow
    final dotGlowPaint = Paint()
      ..color = AppColors.buttonOrange.withAlpha(77)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
    canvas.drawCircle(Offset(centerX, dotY), 6, dotGlowPaint);
  }

  void _drawLampFixture(Canvas canvas, double centerX, double lampY) {
    // Lamp arm (horizontal part at top)
    final armWidth = 100.0;
    final armHeight = 20.0;

    // Lamp housing background
    final lampPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          AppColors.goldSecondary,
          AppColors.goldPrimary,
          const Color(0xFFAA8822),
        ],
      ).createShader(Rect.fromLTWH(centerX - armWidth / 2, lampY, armWidth, armHeight));

    // Draw rounded lamp fixture
    final lampRect = RRect.fromRectAndRadius(
      Rect.fromLTWH(centerX - armWidth / 2, lampY, armWidth, armHeight),
      const Radius.circular(6),
    );
    canvas.drawRRect(lampRect, lampPaint);

    // Glow effect around lamp
    final glowPaint = Paint()
      ..color = AppColors.glowGold.withAlpha(77)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 15);
    canvas.drawRRect(lampRect, glowPaint);

    // Inner light (bright part)
    final innerGlowPaint = Paint()
      ..shader = RadialGradient(
        colors: [
          Colors.white.withAlpha(230),
          AppColors.glowGold.withAlpha(179),
          Colors.transparent,
        ],
        stops: const [0.0, 0.5, 1.0],
      ).createShader(Rect.fromCircle(center: Offset(centerX, lampY + armHeight / 2), radius: 30));

    canvas.drawCircle(Offset(centerX, lampY + armHeight / 2), 30, innerGlowPaint);

    // Lamp rim highlight
    final rimPaint = Paint()
      ..color = AppColors.goldSecondary.withAlpha(204)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;
    canvas.drawRRect(lampRect, rimPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

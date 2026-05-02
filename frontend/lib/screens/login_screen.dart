//screens/login_screen.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/user_session.dart';
import '../services/api_service.dart';
import '../services/push_notifications.dart';
import '../widgets/app_toast.dart';

/// Login screen with email and password fields
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleSignIn() async {
    if (_formKey.currentState!.validate()) {
      final email = _emailController.text.trim();
      final password = _passwordController.text;

      final result = await ApiService.login(email: email, password: password);

      if (!mounted) return;

      if (result['success'] == true) {
        final userData = result['data']['user'];
        final fullName = '${userData['first_name']} ${userData['last_name']}';

        await UserSession.login(name: fullName, email: email);
        await PushNotifications.syncTokenAfterAuth();

        showAppToast(context,
            message: 'Welcome back!',
            isError: false,
            duration: const Duration(seconds: 2));

        Navigator.of(
          context,
        ).pushNamedAndRemoveUntil('/home', (route) => false);
      } else {
        showAppToast(context,
            message: result['error'] ?? 'Login failed', isError: true);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFDF8E8),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFDF8E8),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black87),
          onPressed: () => Navigator.of(context).pop(),
        ),
        centerTitle: true,
        title: Text(
          'Sign In',
          style: GoogleFonts.inter(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: Colors.black87,
          ),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                const SizedBox(height: 30),
                // Building icon
                _buildBuildingIcon(),
                const SizedBox(height: 24),
                // Welcome text
                Text(
                  'Welcome Back',
                  style: GoogleFonts.inter(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF8B4513),
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Manage your urban environment with\nease and precision.',
                  textAlign: TextAlign.center,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    color: Colors.grey[600],
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 40),
                // Email field
                _buildInputField(
                  label: 'Email Address',
                  hint: 'Enter your email',
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter your email';
                    }
                    if (!RegExp(
                      r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$',
                    ).hasMatch(value)) {
                      return 'Please enter a valid email';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 20),
                // Password field
                _buildInputField(
                  label: 'Password',
                  hint: 'Enter your password',
                  controller: _passwordController,
                  obscureText: _obscurePassword,
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword
                          ? Icons.visibility_outlined
                          : Icons.visibility_off_outlined,
                      color: Colors.grey[500],
                    ),
                    onPressed: () {
                      setState(() => _obscurePassword = !_obscurePassword);
                    },
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter your password';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 8),
                // Forgot password
                Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    onPressed: () {
                      Navigator.of(context).pushNamed('/forget-password');
                    },
                    child: Text(
                      'Forgot Password?',
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                        color: const Color(0xFF8B4513),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                // Sign In button
                _buildPrimaryButton(text: 'Sign In', onPressed: _handleSignIn),
                const SizedBox(height: 40),
                // Register link
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      "Don't have an account? ",
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                    GestureDetector(
                      onTap: () {
                        Navigator.of(
                          context,
                        ).pushReplacementNamed('/register_form');
                      },
                      child: Text(
                        'Register',
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF8B4513),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                // City skyline decoration to match registration screen
                _buildCitySkyline(),
                const SizedBox(height: 10),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildBuildingIcon() {
    return ClipOval(
      child: SizedBox(
        width: 80,
        height: 80,
        child: Transform.scale(
          scale: 1.3,
          child: Image.asset('assets/images/logo.jpg', fit: BoxFit.cover),
        ),
      ),
    );
  }

  Widget _buildInputField({
    required String label,
    required String hint,
    required TextEditingController controller,
    TextInputType keyboardType = TextInputType.text,
    bool obscureText = false,
    Widget? suffixIcon,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 14,
            fontWeight: FontWeight.w500,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          keyboardType: keyboardType,
          obscureText: obscureText,
          validator: validator,
          style: GoogleFonts.inter(fontSize: 15, color: Colors.black87),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: GoogleFonts.inter(fontSize: 14, color: Colors.grey[400]),
            filled: true,
            fillColor: Colors.white,
            suffixIcon: suffixIcon,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 16,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFFF9940), width: 2),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Colors.red),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPrimaryButton({
    required String text,
    required VoidCallback onPressed,
  }) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFFFF9940),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(25),
          ),
          elevation: 0,
        ),
        child: Text(
          text,
          style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600),
        ),
      ),
    );
  }

  Widget _buildCitySkyline() {
    return Container(
      height: 80,
      width: double.infinity,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color(0xFFE8D5B5),
            Color(0xFFD4C4A8),
          ],
        ),
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(20),
          topRight: Radius.circular(20),
        ),
      ),
      child: CustomPaint(
        painter: _SkylinePainter(),
      ),
    );
  }
}

class _SkylinePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final skyPaint = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          Color(0xFFE8D5B5),
          Color(0xFFDDCCB8),
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), skyPaint);

    final buildingDark = const Color(0xFFC4A882);
    final buildingMedium = const Color(0xFFD4B894);
    final buildingLight = const Color(0xFFDCC8A8);
    final windowColor = const Color(0xFFB09870);

    _drawBackgroundBuildings(canvas, size, buildingLight);
    _drawMiddleBuildings(canvas, size, buildingMedium, windowColor);
    _drawForegroundBuildings(canvas, size, buildingDark, windowColor);
  }

  void _drawBackgroundBuildings(Canvas canvas, Size size, Color color) {
    final paint = Paint()..color = color.withAlpha(180);

    final buildings = [
      Rect.fromLTWH(size.width * 0.02, size.height * 0.5, size.width * 0.06, size.height * 0.5),
      Rect.fromLTWH(size.width * 0.1, size.height * 0.4, size.width * 0.08, size.height * 0.6),
      Rect.fromLTWH(size.width * 0.25, size.height * 0.45, size.width * 0.05, size.height * 0.55),
      Rect.fromLTWH(size.width * 0.5, size.height * 0.42, size.width * 0.07, size.height * 0.58),
      Rect.fromLTWH(size.width * 0.7, size.height * 0.48, size.width * 0.06, size.height * 0.52),
      Rect.fromLTWH(size.width * 0.85, size.height * 0.44, size.width * 0.08, size.height * 0.56),
    ];

    for (final rect in buildings) {
      canvas.drawRect(rect, paint);
    }
  }

  void _drawMiddleBuildings(Canvas canvas, Size size, Color color, Color windowColor) {
    final paint = Paint()..color = color;
    final windowPaint = Paint()..color = windowColor;

    final b1 = Rect.fromLTWH(size.width * 0.05, size.height * 0.25, size.width * 0.1, size.height * 0.75);
    canvas.drawRect(b1, paint);
    _drawWindows(canvas, b1, windowPaint, 2, 6);

    final b2 = Rect.fromLTWH(size.width * 0.18, size.height * 0.4, size.width * 0.12, size.height * 0.6);
    canvas.drawRect(b2, paint);
    _drawWindows(canvas, b2, windowPaint, 3, 4);

    final b3 = Rect.fromLTWH(size.width * 0.4, size.height * 0.2, size.width * 0.12, size.height * 0.8);
    canvas.drawRect(b3, paint);
    canvas.drawRect(
      Rect.fromLTWH(size.width * 0.455, size.height * 0.12, size.width * 0.01, size.height * 0.08),
      paint,
    );
    _drawWindows(canvas, b3, windowPaint, 3, 7);

    final b4 = Rect.fromLTWH(size.width * 0.65, size.height * 0.35, size.width * 0.1, size.height * 0.65);
    canvas.drawRect(b4, paint);
    _drawWindows(canvas, b4, windowPaint, 2, 5);

    final b5 = Rect.fromLTWH(size.width * 0.82, size.height * 0.3, size.width * 0.11, size.height * 0.7);
    canvas.drawRect(b5, paint);
    _drawWindows(canvas, b5, windowPaint, 2, 6);
  }

  void _drawForegroundBuildings(Canvas canvas, Size size, Color color, Color windowColor) {
    final paint = Paint()..color = color;
    final windowPaint = Paint()..color = windowColor;

    final b1 = Rect.fromLTWH(0, size.height * 0.5, size.width * 0.08, size.height * 0.5);
    canvas.drawRect(b1, paint);

    final b2 = Rect.fromLTWH(size.width * 0.12, size.height * 0.35, size.width * 0.08, size.height * 0.65);
    canvas.drawRect(b2, paint);
    final roofPath = Path()
      ..moveTo(size.width * 0.12, size.height * 0.35)
      ..lineTo(size.width * 0.16, size.height * 0.28)
      ..lineTo(size.width * 0.20, size.height * 0.35)
      ..close();
    canvas.drawPath(roofPath, paint);
    _drawWindows(canvas, b2, windowPaint, 2, 4);

    final b3 = Rect.fromLTWH(size.width * 0.32, size.height * 0.28, size.width * 0.1, size.height * 0.72);
    canvas.drawRect(b3, paint);
    _drawWindows(canvas, b3, windowPaint, 2, 6);

    final b4 = Rect.fromLTWH(size.width * 0.54, size.height * 0.38, size.width * 0.12, size.height * 0.62);
    canvas.drawRect(b4, paint);
    _drawWindows(canvas, b4, windowPaint, 3, 4);

    final b5 = Rect.fromLTWH(size.width * 0.75, size.height * 0.22, size.width * 0.09, size.height * 0.78);
    canvas.drawRect(b5, paint);
    canvas.drawCircle(
      Offset(size.width * 0.795, size.height * 0.24),
      size.width * 0.02,
      Paint()..color = windowColor,
    );
    _drawWindows(canvas, b5, windowPaint, 2, 7);

    final b6 = Rect.fromLTWH(size.width * 0.9, size.height * 0.45, size.width * 0.1, size.height * 0.55);
    canvas.drawRect(b6, paint);
    _drawWindows(canvas, b6, windowPaint, 2, 3);
  }

  void _drawWindows(Canvas canvas, Rect building, Paint paint, int columns, int rows) {
    final windowWidth = building.width / (columns * 2 + 1);
    final windowHeight = building.height / (rows * 2 + 1);

    for (int row = 0; row < rows; row++) {
      for (int col = 0; col < columns; col++) {
        final x = building.left + windowWidth * (col * 2 + 1);
        final y = building.top + windowHeight * (row * 2 + 1);
        canvas.drawRect(
          Rect.fromLTWH(x, y, windowWidth * 0.8, windowHeight * 0.7),
          paint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;

}

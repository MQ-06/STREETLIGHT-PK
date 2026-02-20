//screens/registration_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/user_session.dart';
import '../services/api_service.dart';
/// Registration screen with all required fields
class RegistrationScreen extends StatefulWidget {
  const RegistrationScreen({super.key});

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _cnicController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _cnicController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleCreateAccount() async {
  if (_formKey.currentState!.validate()) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Creating account...')),
    );

    final firstName = _firstNameController.text.trim();
    final lastName = _lastNameController.text.trim();
    final email = _emailController.text.trim();
    final password = _passwordController.text;
    final cnic = _cnicController.text.trim();

    // 🔴 NEW: Call real backend
    final result = await ApiService.signup(
      firstName: firstName,
      lastName: lastName,
      cnic: cnic,
      email: email,
      password: password,
    );

    if (!mounted) return;
    ScaffoldMessenger.of(context).hideCurrentSnackBar();

    if (result['success'] == true) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✓ Account created! Please sign in.'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 2),
        ),
      );
      Navigator.of(context).pushReplacementNamed('/login_form');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['error'] ?? 'Registration failed'),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 3),
        ),
      );
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
          'Registration',
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
                const SizedBox(height: 20),
                // Building icon
                _buildBuildingIcon(),
                const SizedBox(height: 20),
                // Create account text
                Text(
                  'Create Your Account',
                  style: GoogleFonts.inter(
                    fontSize: 26,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  "Join your city's premium urban\nmanagement network and help build a\nsmarter future.",
                  textAlign: TextAlign.center,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    color: Colors.grey[600],
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 30),
                // First Name & Last Name row
                Row(
                  children: [
                    Expanded(
                      child: _buildInputField(
                        label: 'First Name',
                        hint: 'e.g. John',
                        controller: _firstNameController,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Required';
                          }
                          return null;
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildInputField(
                        label: 'Last Name',
                        hint: 'e.g. Doe',
                        controller: _lastNameController,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Required';
                          }
                          return null;
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                // CNIC field
                _buildInputField(
                  label: 'CNIC (Identity Number)',
                  hint: '12345-XXXXXXX-X',
                  controller: _cnicController,
                  keyboardType: TextInputType.number,
                  inputFormatters: [
                    FilteringTextInputFormatter.digitsOnly,
                    LengthLimitingTextInputFormatter(13),
                    _CnicInputFormatter(),
                  ],
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter your CNIC';
                    }
                    // Remove dashes to count digits
                    final digitsOnly = value.replaceAll('-', '');
                    if (digitsOnly.length != 13) {
                      return 'CNIC must be exactly 13 digits';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 20),
                // Email field
                _buildInputField(
                  label: 'Email Address',
                  hint: 'john.doe@city.com',
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter your email';
                    }
                    if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                      return 'Please enter a valid email';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 20),
                // Password field
                _buildInputField(
                  label: 'Password',
                  hint: 'Min. 8 characters',
                  controller: _passwordController,
                  obscureText: _obscurePassword,
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                      color: Colors.grey[500],
                    ),
                    onPressed: () {
                      setState(() => _obscurePassword = !_obscurePassword);
                    },
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter a password';
                    }
                    if (value.length < 8) {
                      return 'Password must be at least 8 characters';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 30),
                // Create Account button
                _buildPrimaryButton(
                  text: 'Create Account',
                  onPressed: _handleCreateAccount,
                ),
                const SizedBox(height: 20),
                // Terms text
                RichText(
                  textAlign: TextAlign.center,
                  text: TextSpan(
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                    children: [
                      const TextSpan(text: 'By clicking "Create Account", you agree to our '),
                      TextSpan(
                        text: 'Terms of\nService',
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: const Color(0xFF2196F3),
                          decoration: TextDecoration.underline,
                        ),
                      ),
                      const TextSpan(text: ' and '),
                      TextSpan(
                        text: 'Privacy Policy',
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: const Color(0xFF2196F3),
                          decoration: TextDecoration.underline,
                        ),
                      ),
                      const TextSpan(text: '.'),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Sign in link
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Already have an account? ',
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                    GestureDetector(
                      onTap: () {
                        Navigator.of(context).pushReplacementNamed('/login_form');
                      },
                      child: Text(
                        'Sign In',
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF2196F3),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                // City skyline decoration
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
          child: Image.asset(
            'assets/images/logo.jpg',
            fit: BoxFit.cover,
          ),
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
    List<TextInputFormatter>? inputFormatters,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 13,
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
          inputFormatters: inputFormatters,
          style: GoogleFonts.inter(fontSize: 14, color: Colors.black87),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: GoogleFonts.inter(
              fontSize: 14,
              color: Colors.grey[400],
            ),
            filled: true,
            fillColor: Colors.white,
            suffixIcon: suffixIcon,
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Color(0xFFFF9940), width: 2),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
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
          style: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
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

/// Custom formatter for CNIC with dashes (XXXXX-XXXXXXX-X)
class _CnicInputFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    final text = newValue.text;
    if (text.isEmpty) return newValue;

    final buffer = StringBuffer();
    for (int i = 0; i < text.length; i++) {
      if (i == 5 || i == 12) {
        buffer.write('-');
      }
      buffer.write(text[i]);
    }

    final newText = buffer.toString();
    return TextEditingValue(
      text: newText,
      selection: TextSelection.collapsed(offset: newText.length),
    );
  }
}

/// Custom painter for city skyline silhouette - more realistic version
class _SkylinePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // Background gradient sky effect
    final skyPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          const Color(0xFFE8D5B5).withAlpha(0),
          const Color(0xFFDDCCB8),
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), skyPaint);

    // Building colors
    final buildingDark = const Color(0xFFC4A882);
    final buildingMedium = const Color(0xFFD4B894);
    final buildingLight = const Color(0xFFDCC8A8);
    final windowColor = const Color(0xFFB09870);

    // Draw multiple layers of buildings for depth
    _drawBackgroundBuildings(canvas, size, buildingLight);
    _drawMiddleBuildings(canvas, size, buildingMedium, windowColor);
    _drawForegroundBuildings(canvas, size, buildingDark, windowColor);
  }

  void _drawBackgroundBuildings(Canvas canvas, Size size, Color color) {
    final paint = Paint()..color = color.withAlpha(180);
    
    // Distant buildings (smaller, lighter)
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
    
    // Middle layer buildings
    // Building 1 - Left tall building
    final b1 = Rect.fromLTWH(size.width * 0.05, size.height * 0.25, size.width * 0.1, size.height * 0.75);
    canvas.drawRect(b1, paint);
    _drawWindows(canvas, b1, windowPaint, 2, 6);
    
    // Building 2 - Wide building
    final b2 = Rect.fromLTWH(size.width * 0.18, size.height * 0.4, size.width * 0.12, size.height * 0.6);
    canvas.drawRect(b2, paint);
    _drawWindows(canvas, b2, windowPaint, 3, 4);
    
    // Building 3 - Center tall
    final b3 = Rect.fromLTWH(size.width * 0.4, size.height * 0.2, size.width * 0.12, size.height * 0.8);
    canvas.drawRect(b3, paint);
    // Add antenna/spire
    canvas.drawRect(
      Rect.fromLTWH(size.width * 0.455, size.height * 0.12, size.width * 0.01, size.height * 0.08),
      paint,
    );
    _drawWindows(canvas, b3, windowPaint, 3, 7);
    
    // Building 4 - Right side
    final b4 = Rect.fromLTWH(size.width * 0.65, size.height * 0.35, size.width * 0.1, size.height * 0.65);
    canvas.drawRect(b4, paint);
    _drawWindows(canvas, b4, windowPaint, 2, 5);
    
    // Building 5 - Far right
    final b5 = Rect.fromLTWH(size.width * 0.82, size.height * 0.3, size.width * 0.11, size.height * 0.7);
    canvas.drawRect(b5, paint);
    _drawWindows(canvas, b5, windowPaint, 2, 6);
  }

  void _drawForegroundBuildings(Canvas canvas, Size size, Color color, Color windowColor) {
    final paint = Paint()..color = color;
    final windowPaint = Paint()..color = windowColor;
    
    // Foreground buildings (larger, more detail)
    // Building 1 - Left corner
    final b1 = Rect.fromLTWH(0, size.height * 0.5, size.width * 0.08, size.height * 0.5);
    canvas.drawRect(b1, paint);
    
    // Building 2 - Second from left with rooftop
    final b2 = Rect.fromLTWH(size.width * 0.12, size.height * 0.35, size.width * 0.08, size.height * 0.65);
    canvas.drawRect(b2, paint);
    // Rooftop detail
    final roofPath = Path();
    roofPath.moveTo(size.width * 0.12, size.height * 0.35);
    roofPath.lineTo(size.width * 0.16, size.height * 0.28);
    roofPath.lineTo(size.width * 0.20, size.height * 0.35);
    roofPath.close();
    canvas.drawPath(roofPath, paint);
    _drawWindows(canvas, b2, windowPaint, 2, 4);
    
    // Building 3 - Center modern
    final b3 = Rect.fromLTWH(size.width * 0.32, size.height * 0.28, size.width * 0.1, size.height * 0.72);
    canvas.drawRect(b3, paint);
    _drawWindows(canvas, b3, windowPaint, 2, 6);
    
    // Building 4 - Center right
    final b4 = Rect.fromLTWH(size.width * 0.54, size.height * 0.38, size.width * 0.12, size.height * 0.62);
    canvas.drawRect(b4, paint);
    _drawWindows(canvas, b4, windowPaint, 3, 4);
    
    // Building 5 - Right modern tower
    final b5 = Rect.fromLTWH(size.width * 0.75, size.height * 0.22, size.width * 0.09, size.height * 0.78);
    canvas.drawRect(b5, paint);
    // Add helipad on roof
    canvas.drawCircle(
      Offset(size.width * 0.795, size.height * 0.24),
      size.width * 0.02,
      Paint()..color = windowColor,
    );
    _drawWindows(canvas, b5, windowPaint, 2, 7);
    
    // Building 6 - Right corner
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

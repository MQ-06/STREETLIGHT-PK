import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'screens/splash_screen.dart';
import 'screens/landing_screen.dart';
import 'screens/login_screen.dart';
import 'screens/registration_screen.dart';
import 'screens/home_screen.dart';
import 'screens/explore_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/report_issue_screen.dart';
import 'screens/forget-password.dart';    // ✅ fixed: was forget-passsword.dart (3 s's + hyphen)
import 'screens/reset-password.dart';     // ✅ fixed: was reset-password.dart (hyphen)
import 'theme/app_colors.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: AppColors.background,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );

  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  runApp(const StreetlightApp());
}

class StreetlightApp extends StatelessWidget {
  const StreetlightApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Streetlight',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: AppColors.background,
        primaryColor: AppColors.goldPrimary,
        colorScheme: ColorScheme.dark(
          primary: AppColors.goldPrimary,
          secondary: AppColors.goldSecondary,
          surface: AppColors.darkBrown,
        ),
        fontFamily: 'Roboto',
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashScreen(),
        '/landing': (context) => const LandingScreen(),
        '/login_form': (context) => const LoginScreen(),
        '/register_form': (context) => const RegistrationScreen(),
        '/home': (context) => const HomeScreen(),
        '/explore': (context) => const ExploreScreen(),
        '/profile': (context) => const ProfileScreen(),
        '/report_issue': (context) => const ReportIssueScreen(),
        '/forget-password': (context) => const ForgotPasswordScreen(),   // ✅ NEW
        '/reset-password': (context) => const ResetPasswordScreen(),     // ✅ NEW
      },
    );
  }
}



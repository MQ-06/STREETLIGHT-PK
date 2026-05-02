import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_core/firebase_core.dart';
import 'services/push_notifications.dart';
import 'screens/splash_screen.dart';
import 'screens/landing_screen.dart';
import 'screens/login_screen.dart';
import 'screens/registration_screen.dart';
import 'screens/main_shell.dart';
import 'screens/report_issue_screen.dart';
import 'screens/verification_screen.dart';
import 'screens/notifications_screen.dart';
import 'screens/resolution_confirm_screen.dart';
import 'screens/forget-password.dart';    // ✅ fixed: was forget-passsword.dart (3 s's + hyphen)
import 'screens/reset-password.dart';     // ✅ fixed: was reset-password.dart (hyphen)
import 'theme/app_colors.dart';

final GlobalKey<NavigatorState> _navKey = GlobalKey<NavigatorState>();

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  await PushNotifications.init(
    onNavigate: (route, data) async {
      final nav = _navKey.currentState;
      if (nav == null) return;
      final type = data['type']?.toString();
      if (route == '/verification' || type == 'VERIFY_REQUEST') {
        nav.pushNamed('/verification');
        return;
      }
      if (route == '/resolution_confirm' ||
          type == 'RESOLUTION_CONFIRM' ||
          type == 'CONFIRM_OR_REJECT') {
        final rid = int.tryParse('${data['report_id'] ?? ''}');
        if (rid != null && rid > 0) {
          nav.pushNamed('/resolution_confirm', arguments: {'report_id': rid});
        }
        return;
      }
      if (route == '/notifications') {
        nav.pushNamed('/notifications');
      } else {
        nav.pushNamed(route);
      }
    },
  );

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
      navigatorKey: _navKey,
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
        '/home': (context) => const MainShell(),
        '/report_issue': (context) => const ReportIssueScreen(),
        '/forget-password': (context) => const ForgotPasswordScreen(),   // ✅ NEW
        '/reset-password': (context) => const ResetPasswordScreen(),     // ✅ NEW
        '/verification': (context) => const VerificationScreen(),
        '/notifications': (context) => const NotificationsScreen(),
        '/resolution_confirm': (context) {
          final args = ModalRoute.of(context)?.settings.arguments;
          var rid = 0;
          if (args is Map && args['report_id'] != null) {
            final v = args['report_id'];
            rid = v is int ? v : (int.tryParse('$v') ?? 0);
          }
          return ResolutionConfirmScreen(reportId: rid);
        },
      },
    );
  }
}



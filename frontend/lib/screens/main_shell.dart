import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'home_screen.dart';
import 'explore_screen.dart';
import 'profile_screen.dart';
import 'report_issue_screen.dart';
import '../services/api_service.dart';
import '../services/push_notifications.dart';

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _currentIndex = 0;

  late final List<Widget> _pages;
  final GlobalKey<HomeScreenState> _homeKey = GlobalKey<HomeScreenState>();
  final ValueNotifier<int> _homeUnreadBadge = ValueNotifier<int>(0);

  @override
  void initState() {
    super.initState();
    // Create once so state inside each tab is preserved via IndexedStack
    _pages = [
      HomeScreen(key: _homeKey, unreadBadgeNotifier: _homeUnreadBadge),
      ExploreScreen(),
      ReportIssueScreen(
        fromTab: true,
        onBack: () {
          setState(() => _currentIndex = 0);
        },
        onSubmitted: () {
          // Switch back to Home and refresh the feed so the new report appears.
          setState(() => _currentIndex = 0);
          WidgetsBinding.instance.addPostFrameCallback((_) {
            _homeKey.currentState?.reloadFeed();
          });
        },
      ),
      ProfileScreen(),
    ];
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final t = await ApiService.getToken();
      if (t != null && t.isNotEmpty) {
        await PushNotifications.syncTokenAfterAuth();
      }
    });
  }

  @override
  void dispose() {
    _homeUnreadBadge.dispose();
    super.dispose();
  }

  void _onTabTapped(int index) {
    if (index == _currentIndex) return;
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _pages,
      ),
      bottomNavigationBar: _buildBottomNavBar(),
    );
  }

  Widget _buildBottomNavBar() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(Icons.home_outlined, 'HOME', 0),
              _buildNavItem(Icons.explore, 'EXPLORE', 1),
              _buildNavItem(Icons.add_circle_outline, 'REPORT', 2),
              _buildNavItem(Icons.person_outline, 'PROFILE', 3),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label, int index) {
    final isActive = index == _currentIndex;
    final Color activeColor = const Color(0xFFC85A3A);
    final Color inactiveColor = const Color(0xFF666666);

    Widget iconWidget = Icon(
      icon,
      color: isActive ? activeColor : inactiveColor,
      size: 24,
    );

    if (index == 0) {
      iconWidget = ValueListenableBuilder<int>(
        valueListenable: _homeUnreadBadge,
        builder: (context, count, child) {
          return Badge(
            backgroundColor: activeColor,
            padding: const EdgeInsets.symmetric(horizontal: 4),
            isLabelVisible: count > 0,
            label: Text(
              count > 99 ? '99+' : '$count',
              style: GoogleFonts.roboto(
                fontSize: 9,
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            child: child,
          );
        },
        child: iconWidget,
      );
    }

    return GestureDetector(
      onTap: () => _onTabTapped(index),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          iconWidget,
          const SizedBox(height: 4),
          Text(
            label,
            style: GoogleFonts.roboto(
              fontSize: 10,
              fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
              color: isActive ? activeColor : inactiveColor,
            ),
          ),
        ],
      ),
    );
  }
}


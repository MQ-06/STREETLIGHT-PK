import 'package:flutter/material.dart';

import '../widgets/notifications_modal.dart';

/// Route wrapper: shows the notifications modal when navigated to (e.g. from push tap).
/// When modal is dismissed, pops this route.
class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  bool _modalShown = false;

  @override
  Widget build(BuildContext context) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || _modalShown) return;
      _modalShown = true;
      showNotificationsModal(context, onDismiss: () {
        if (mounted) Navigator.pop(context);
      });
    });
    return const Scaffold(
      backgroundColor: Colors.transparent,
      body: SizedBox.shrink(),
    );
  }
}


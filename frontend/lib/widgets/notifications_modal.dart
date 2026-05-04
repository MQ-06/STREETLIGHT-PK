import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../models/notification_model.dart';
import '../services/api_service.dart';
import '../theme/app_colors.dart';

/// Shows notifications in a modal bottom sheet.
/// Pass [onDismiss] to refresh unread count when modal closes.
void showNotificationsModal(
  BuildContext context, {
  VoidCallback? onDismiss,
}) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (ctx) => DraggableScrollableSheet(
      initialChildSize: 0.85,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      builder: (_, controller) => Container(
        decoration: const BoxDecoration(
          color: AppColors.background,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          children: [
            const SizedBox(height: 12),
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.white24,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
              child: Row(
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Notifications',
                        style: GoogleFonts.poppins(
                          fontWeight: FontWeight.w600,
                          fontSize: 18,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        'Community alerts',
                        style: GoogleFonts.roboto(
                          fontSize: 10,
                          color: Colors.white54,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),
                  // Always show Verification Feed button in header
                  TextButton.icon(
                    onPressed: () {
                      Navigator.pop(ctx);
                      Navigator.pushNamed(context, '/verification');
                    },
                    icon: const Icon(Icons.check_circle_outline, size: 14, color: AppColors.goldSecondary),
                    label: Text(
                      'VERIFY',
                      style: GoogleFonts.rajdhani(
                        color: AppColors.goldSecondary,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                        letterSpacing: 1.0,
                      ),
                    ),
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      backgroundColor: Colors.white.withOpacity(0.05),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white70),
                    onPressed: () {
                      Navigator.pop(ctx);
                      onDismiss?.call();
                    },
                  ),
                ],
              ),
            ),
            Expanded(
              child: NotificationsModalContent(
                scrollController: controller,
                onDismiss: () {
                  Navigator.pop(ctx);
                  onDismiss?.call();
                },
              ),
            ),
          ],
        ),
      ),
    ),
  ).whenComplete(() => onDismiss?.call());
}

class NotificationsModalContent extends StatefulWidget {
  final ScrollController scrollController;
  final VoidCallback? onDismiss;

  const NotificationsModalContent({
    super.key,
    required this.scrollController,
    this.onDismiss,
  });

  @override
  State<NotificationsModalContent> createState() =>
      _NotificationsModalContentState();
}

class _NotificationsModalContentState extends State<NotificationsModalContent> {
  bool _loading = true;
  String? _error;
  List<AppNotification> _items = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    final res = await ApiService.getNotifications(limit: 100);
    if (!mounted) return;

    if (res['success'] == true) {
      final data = res['data'] as Map<String, dynamic>;
      final list = (data['notifications'] as List? ?? const [])
          .whereType<Map>()
          .map((e) => AppNotification.fromJson(Map<String, dynamic>.from(e)))
          .toList();
      setState(() {
        _items = list;
        _loading = false;
      });
    } else {
      setState(() {
        _error = (res['error'] ?? 'Failed').toString();
        _loading = false;
      });
    }
  }

  Future<void> _markRead(AppNotification n, bool read) async {
    final res = await ApiService.markNotificationRead(n.id, read: read);
    if (res['success'] == true) {
      await _load();
    }
  }

  int _resolutionReportId(AppNotification n) {
    final e = n.entityId;
    if (e != null && e > 0) return e;
    final d = n.data;
    if (d == null) return 0;
    final v = d['report_id'];
    if (v is int) return v;
    return int.tryParse('$v') ?? 0;
  }

  Future<void> _open(AppNotification n) async {
    final rootNav = Navigator.of(context, rootNavigator: true);
    if (!n.isRead) {
      await _markRead(n, true);
    }
    if (!mounted) return;
    Navigator.pop(context); // close the modal sheet
    widget.onDismiss?.call();

    if (n.type == 'VERIFY_REQUEST') {
      rootNav.pushNamed('/verification');
      return;
    }

    if (n.type == 'RESOLUTION_CONFIRM' ||
        n.type == 'CONFIRM_OR_REJECT') {
      final rid = _resolutionReportId(n);
      if (rid > 0) {
        rootNav.pushNamed(
          '/resolution_confirm',
          arguments: {'report_id': rid},
        );
      }
      return;
    }
  }

  String _formatTime(DateTime dt) {
    final local = dt.toLocal();
    final now = DateTime.now();
    final diff = now.difference(local);
    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${local.day}/${local.month}/${local.year}';
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(
            _error!,
            style: GoogleFonts.roboto(color: Colors.white70),
            textAlign: TextAlign.center,
          ),
        ),
      );
    }
    if (_items.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 40),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.notifications_off_outlined,
                  size: 52, color: Colors.white.withOpacity(0.5)),
              const SizedBox(height: 16),
              Text(
                "You're all caught up!",
                textAlign: TextAlign.center,
                style: GoogleFonts.roboto(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.5,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                "No new notifications for you right now.",
                textAlign: TextAlign.center,
                style: GoogleFonts.roboto(
                  color: Colors.white70,
                  fontSize: 13,
                  height: 1.5,
                ),
              ),
            ],
          ),
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.separated(
        controller: widget.scrollController,
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
        itemBuilder: (context, index) {
          final n = _items[index];
          return InkWell(
            onTap: () => _open(n),
            borderRadius: BorderRadius.circular(14),
            child: Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: n.isRead
                    ? AppColors.darkBrown.withOpacity(0.55)
                    : AppColors.darkBrown,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: n.isRead
                      ? Colors.transparent
                      : AppColors.goldSecondary.withOpacity(0.35),
                ),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    margin: const EdgeInsets.only(top: 6),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: n.isRead
                          ? Colors.white24
                          : AppColors.goldSecondary,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          n.title,
                          style: GoogleFonts.roboto(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        ),
                        if ((n.body ?? '').trim().isNotEmpty) ...[
                          const SizedBox(height: 4),
                          Text(
                            n.body!,
                            style: GoogleFonts.roboto(
                              fontSize: 12,
                              color: Colors.white70,
                              height: 1.35,
                            ),
                          ),
                        ],
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            Text(
                              _formatTime(n.createdAt),
                              style: GoogleFonts.roboto(
                                fontSize: 11,
                                color: Colors.white54,
                              ),
                            ),
                            const Spacer(),
                            TextButton(
                              onPressed: () => _markRead(n, !n.isRead),
                              child: Text(
                                n.isRead ? 'Mark unread' : 'Mark read',
                                style: GoogleFonts.roboto(
                                  fontSize: 11,
                                  color: AppColors.goldSecondary,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        },
        separatorBuilder: (_, __) => const SizedBox(height: 10),
        itemCount: _items.length,
      ),
    );
  }
}

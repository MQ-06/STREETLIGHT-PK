import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../models/notification_model.dart';
import '../services/api_service.dart';
import '../theme/app_colors.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
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

  Future<void> _open(AppNotification n) async {
    if (!n.isRead) {
      await _markRead(n, true);
    }

    // Minimal deep link logic for Phase 1 (no push yet)
    if (n.type == 'VERIFY_REQUEST') {
      if (!mounted) return;
      await Navigator.pushNamed(context, '/verification');
      return;
    }
    // For REPORT_STATUS etc: stay in the list for now
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        title: Text(
          'Notifications',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w600),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? ListView(
                    children: [
                      const SizedBox(height: 80),
                      Center(
                        child: Text(
                          _error!,
                          style: GoogleFonts.roboto(color: Colors.white70),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ],
                  )
                : _items.isEmpty
                    ? ListView(
                        children: [
                          const SizedBox(height: 80),
                          Icon(Icons.notifications_off_outlined,
                              size: 52, color: Colors.white.withOpacity(0.5)),
                          const SizedBox(height: 10),
                          Center(
                            child: Text(
                              "You're all caught up!",
                              style: GoogleFonts.roboto(
                                  color: Colors.white70, fontSize: 14),
                            ),
                          ),
                        ],
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 12),
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
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
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
      ),
    );
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
}


// lib/screens/home_screen.dart
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/comment_model.dart';
import '../models/report_model.dart';
// Verification feed moved to Notifications screen; keep home focused on feed.
import '../services/api_service.dart';
import 'report_issue_screen.dart';
import '../widgets/notifications_modal.dart';

class HomeColors {
  static const backgroundColor = Color(0xFFFFF8E7);
  static const cardBackground = Color(0xFFFFFFFF);
  static const statusOrange = Color(0xFFC85A3A);
  static const statusGreen = Color(0xFF2E7D32);
  static const statusGreenLight = Color(0xFFE8F5E9);
  static const statusRed = Color(0xFFD32F2F);
  static const textPrimary = Color(0xFF000000);
  static const textSecondary = Color(0xFF666666);
  static const textGray = Color(0xFFAAAAAA);
  static const borderColor = Color(0xFFEEEEEE);
}

class HomeScreen extends StatefulWidget {
  /// When set (e.g. by [MainShell]), unread count is mirrored for tab-bar badges.
  final ValueNotifier<int>? unreadBadgeNotifier;

  const HomeScreen({super.key, this.unreadBadgeNotifier});

  @override
  State<HomeScreen> createState() => HomeScreenState();
}

class HomeScreenState extends State<HomeScreen> with WidgetsBindingObserver {
  final TextEditingController _searchController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  Timer? _feedPollTimer;

  List<ReportModel> _reports = [];
  String _searchQuery = '';
  bool _isLoading = true;
  String? _errorMessage;
  int _pageIndex = 1;
  static const int _pageSize = 20;
  bool _hasMore = true;
  // Prevent older feed requests from overwriting fresher results.
  int _feedRequestId = 0;

  int _unreadNotificationCount = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _loadFeed(refresh: true);
    _loadUnreadNotificationCount();
    
    // Add scroll listener for infinite scroll
    _scrollController.addListener(() {
      if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 200) {
        if (!_isLoading && _hasMore) {
          _pageIndex++;
          _loadFeed(refresh: false);
        }
      }
    });

    _feedPollTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (!mounted) return;
      // Background poll only refreshes the first page
      if (_scrollController.position.pixels < 100) {
        _loadFeed(refresh: true);
      }
    });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      _loadFeed(refresh: true);
      _loadUnreadNotificationCount();
    }
  }

  Future<void> _loadUnreadNotificationCount() async {
    final res = await ApiService.getUnreadNotificationCount();
    if (!mounted) return;
    if (res['success'] == true) {
      final data = res['data'] as Map<String, dynamic>;
      final n =
          (data['unread_count'] as int?) ?? int.tryParse('${data['unread_count']}') ?? 0;
      setState(() => _unreadNotificationCount = n);
      widget.unreadBadgeNotifier?.value = n;
    }
  }

  @override
  void dispose() {
    _feedPollTimer?.cancel();
    WidgetsBinding.instance.removeObserver(this);
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // ─────────────────────────────────────────────
  // DATA
  // ─────────────────────────────────────────────

  Future<void> _loadFeed({bool refresh = false}) async {
    final requestId = ++_feedRequestId;
    if (refresh) {
      _pageIndex = 1;
      _hasMore = true;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final skip = (_pageIndex - 1) * _pageSize;
    final result = await ApiService.getReportsFeed(
      skip: skip,
      limit: _pageSize,
    );

    if (!mounted) return;
    if (requestId != _feedRequestId) return; // stale response

    if (result['success'] == true) {
      final raw = result['data']['reports'] as List<dynamic>;
      final newReports = raw.map((r) => ReportModel.fromJson(r)).toList();
      setState(() {
        if (refresh) {
          _reports = newReports;
        } else {
          _reports.addAll(newReports);
        }
        _hasMore = newReports.length == _pageSize;
        _isLoading = false;
      });
    } else {
      // Session expired → unified logout flow
      if (result['code'] == 401) {
        await ApiService.logout();
        if (mounted) {
          Navigator.pushNamedAndRemoveUntil(
            context,
            '/login_form',
            (route) => false,
          );
        }
        return;
      }
      if (requestId != _feedRequestId) return; // stale response
      setState(() {
        _errorMessage = result['error'];
        _isLoading = false;
      });
    }
  }


  /// Used by [MainShell] when the report form is submitted from the tab.
  Future<void> reloadFeed() async {
    setState(() => _pageIndex = 1);
    await _loadFeed(refresh: true);
  }

  // ─────────────────────────────────────────────
  // SUPPORT / VERIFY — optimistic UI
  // ─────────────────────────────────────────────

  Future<void> _onSupportTap(int index) async {
    final report = _reports[index];
    final wasSupported = report.hasSupported;
    final prevCount = report.supportCount;

    // Optimistic update immediately
    setState(() {
      report.hasSupported = !wasSupported;
      _reports[index] = ReportModel(
        id: report.id,
        reporterId: report.reporterId,
        reporterName: report.reporterName,
        reporterInitials: report.reporterInitials,
        reporterAvatarUrl: report.reporterAvatarUrl,
        timestamp: report.timestamp,
        location: report.location,
        locationCity: report.locationCity,
        issueCategory: report.issueCategory,
        title: report.title,
        description: report.description,
        imageUrl: report.imageUrl,
        views: report.views,
        supportCount: wasSupported ? prevCount - 1 : prevCount + 1,
        verifyCount: report.verifyCount,
        commentCount: report.commentCount,
        status: report.status,
        kanbanStage: report.kanbanStage,
        combinedScore: report.combinedScore,
        verificationStatus: report.verificationStatus,
        locationLat: report.locationLat,
        locationLng: report.locationLng,
        hasSupported: !wasSupported,
        hasVerified: report.hasVerified,
      );
    });

    final result = await ApiService.toggleSupport(report.id);
    if (!mounted) return;

    if (result['success'] == true) {
      // Sync exact count from server
      final data = result['data'];
      final idx = _reports.indexWhere((r) => r.id == report.id);
      if (idx != -1) {
        setState(() {
          final r = _reports[idx];
          _reports[idx] = ReportModel(
            id: r.id,
            reporterId: r.reporterId,
            reporterName: r.reporterName,
            reporterInitials: r.reporterInitials,
            reporterAvatarUrl: r.reporterAvatarUrl,
            timestamp: r.timestamp,
            location: r.location,
            locationCity: r.locationCity,
            issueCategory: r.issueCategory,
            title: r.title,
            description: r.description,
            imageUrl: r.imageUrl,
            views: r.views,
            supportCount: data['support_count'] as int,
            verifyCount: r.verifyCount,
            commentCount: r.commentCount,
            status: r.status,
            kanbanStage: r.kanbanStage,
            combinedScore: r.combinedScore,
            verificationStatus: r.verificationStatus,
            locationLat: r.locationLat,
            locationLng: r.locationLng,
            hasSupported: data['has_supported'] as bool,
            hasVerified: r.hasVerified,
          );
        });
      }
    } else {
      // Revert on failure
      final idx = _reports.indexWhere((r) => r.id == report.id);
      if (idx != -1) {
        setState(() {
          final r = _reports[idx];
          _reports[idx] = ReportModel(
            id: r.id,
            reporterId: r.reporterId,
            reporterName: r.reporterName,
            reporterInitials: r.reporterInitials,
            reporterAvatarUrl: r.reporterAvatarUrl,
            timestamp: r.timestamp,
            location: r.location,
            locationCity: r.locationCity,
            issueCategory: r.issueCategory,
            title: r.title,
            description: r.description,
            imageUrl: r.imageUrl,
            views: r.views,
            supportCount: prevCount,
            verifyCount: r.verifyCount,
            commentCount: r.commentCount,
            status: r.status,
            kanbanStage: r.kanbanStage,
            combinedScore: r.combinedScore,
            verificationStatus: r.verificationStatus,
            locationLat: r.locationLat,
            locationLng: r.locationLng,
            hasSupported: wasSupported,
            hasVerified: r.hasVerified,
          );
        });
      }
    }
  }

  Future<void> _onVerifyTap(int index) async {
    final report = _reports[index];
    final wasVerified = report.hasVerified;
    final prevCount = report.verifyCount;

    // Optimistic update
    setState(() {
      _reports[index] = ReportModel(
        id: report.id,
        reporterId: report.reporterId,
        reporterName: report.reporterName,
        reporterInitials: report.reporterInitials,
        reporterAvatarUrl: report.reporterAvatarUrl,
        timestamp: report.timestamp,
        location: report.location,
        locationCity: report.locationCity,
        issueCategory: report.issueCategory,
        title: report.title,
        description: report.description,
        imageUrl: report.imageUrl,
        views: report.views,
        supportCount: report.supportCount,
        verifyCount: wasVerified ? prevCount - 1 : prevCount + 1,
        commentCount: report.commentCount,
        status: report.status,
        kanbanStage: report.kanbanStage,
        combinedScore: report.combinedScore,
        verificationStatus: report.verificationStatus,
        locationLat: report.locationLat,
        locationLng: report.locationLng,
        hasSupported: report.hasSupported,
        hasVerified: !wasVerified,
      );
    });

    final result = await ApiService.toggleVerify(report.id);
    if (!mounted) return;

    if (result['success'] == true) {
      final data = result['data'];
      final idx = _reports.indexWhere((r) => r.id == report.id);
      if (idx != -1) {
        setState(() {
          final r = _reports[idx];
          _reports[idx] = ReportModel(
            id: r.id,
            reporterId: r.reporterId,
            reporterName: r.reporterName,
            reporterInitials: r.reporterInitials,
            reporterAvatarUrl: r.reporterAvatarUrl,
            timestamp: r.timestamp,
            location: r.location,
            locationCity: r.locationCity,
            issueCategory: r.issueCategory,
            title: r.title,
            description: r.description,
            imageUrl: r.imageUrl,
            views: r.views,
            supportCount: r.supportCount,
            verifyCount: data['verify_count'] as int,
            commentCount: r.commentCount,
            status: r.status,
            kanbanStage: r.kanbanStage,
            combinedScore: r.combinedScore,
            verificationStatus: r.verificationStatus,
            locationLat: r.locationLat,
            locationLng: r.locationLng,
            hasSupported: r.hasSupported,
            hasVerified: data['has_verified'] as bool,
          );
        });
      }
    } else {
      // Revert
      final idx = _reports.indexWhere((r) => r.id == report.id);
      if (idx != -1) {
        setState(() {
          final r = _reports[idx];
          _reports[idx] = ReportModel(
            id: r.id,
            reporterId: r.reporterId,
            reporterName: r.reporterName,
            reporterInitials: r.reporterInitials,
            reporterAvatarUrl: r.reporterAvatarUrl,
            timestamp: r.timestamp,
            location: r.location,
            locationCity: r.locationCity,
            issueCategory: r.issueCategory,
            title: r.title,
            description: r.description,
            imageUrl: r.imageUrl,
            views: r.views,
            supportCount: r.supportCount,
            verifyCount: prevCount,
            commentCount: r.commentCount,
            status: r.status,
            kanbanStage: r.kanbanStage,
            combinedScore: r.combinedScore,
            verificationStatus: r.verificationStatus,
            locationLat: r.locationLat,
            locationLng: r.locationLng,
            hasSupported: r.hasSupported,
            hasVerified: wasVerified,
          );
        });
      }
    }
  }

  // ─────────────────────────────────────────────
  // BUILD
  // ─────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: HomeColors.backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            _buildAppHeader(),
            _buildSearchBar(),
            Expanded(child: _buildBody()),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const ReportIssueScreen()),
          );
          if (result == true) {
            setState(() => _pageIndex = 1);
            await _loadFeed(refresh: true);
          }
        },
        backgroundColor: HomeColors.statusOrange,
        child: const Icon(Icons.add, color: Colors.white, size: 28),
      ),
    );
  }


  Widget _buildBody() {
    // Apply search filtering
    final List<ReportModel> visibleReports;
    if (_searchQuery.isEmpty) {
      visibleReports = _reports;
    } else {
      final q = _searchQuery;
      visibleReports = _reports.where((r) {
        return r.title.toLowerCase().contains(q) ||
            r.description.toLowerCase().contains(q) ||
            r.location.toLowerCase().contains(q) ||
            r.locationCity.toLowerCase().contains(q) ||
            r.reporterName.toLowerCase().contains(q);
      }).toList();
    }

    // Loading state
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: HomeColors.statusOrange),
      );
    }

    // Error state
    if (_errorMessage != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.cloud_off, size: 64, color: HomeColors.textGray),
              const SizedBox(height: 16),
              Text(
                _errorMessage!,
                textAlign: TextAlign.center,
                style: GoogleFonts.roboto(
                    fontSize: 14, color: HomeColors.textSecondary),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => _loadFeed(refresh: true),
                style: ElevatedButton.styleFrom(
                    backgroundColor: HomeColors.statusOrange),
                child: Text('Retry',
                    style: GoogleFonts.roboto(color: Colors.white)),
              ),
            ],
          ),
        ),
      );
    }

    // Empty state
    if (visibleReports.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.inbox_outlined,
                size: 64, color: HomeColors.textGray),
            const SizedBox(height: 16),
            Text(
              _searchQuery.isEmpty
                  ? 'No reports yet.\nBe the first to report an issue!'
                  : 'No reports match your search.\nTry a different area or keyword.',
              textAlign: TextAlign.center,
              style: GoogleFonts.roboto(
                  fontSize: 15, color: HomeColors.textSecondary),
            ),
          ],
        ),
      );
    }

    // Feed
    return RefreshIndicator(
      color: HomeColors.statusOrange,
      onRefresh: () => _loadFeed(refresh: true),
      child: ListView.builder(
        controller: _scrollController,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: visibleReports.length + (_hasMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == visibleReports.length) {
            return const Padding(
              padding: EdgeInsets.symmetric(vertical: 16),
              child: Center(
                child: CircularProgressIndicator(color: HomeColors.statusOrange),
              ),
            );
          }
          return _buildReportCard(visibleReports, index);
        },
      ),
    );
  }

  // ─────────────────────────────────────────────
  // HEADER & SEARCH
  // ─────────────────────────────────────────────

  Widget _buildAppHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          ClipOval(
            child: SizedBox(
              width: 36,
              height: 36,
              child: Transform.scale(
                scale: 1.3,
                child:
                    Image.asset('assets/images/logo.jpg', fit: BoxFit.cover),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Text(
            'STREETLIGHT',
            style: GoogleFonts.poppins(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: HomeColors.textPrimary,
                letterSpacing: 1.2),
          ),
          const Spacer(),
          Builder(
            builder: (context) => Badge(
              backgroundColor: HomeColors.statusOrange,
              padding: const EdgeInsets.symmetric(horizontal: 5),
              isLabelVisible: _unreadNotificationCount > 0,
              label: Text(
                _unreadNotificationCount > 99 ? '99+' : '$_unreadNotificationCount',
                style: GoogleFonts.roboto(
                  fontSize: 10,
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              child: IconButton(
                icon: const Icon(Icons.notifications_outlined,
                    color: HomeColors.textSecondary),
                onPressed: () {
                  showNotificationsModal(context, onDismiss: _loadUnreadNotificationCount);
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: Container(
              height: 48,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: HomeColors.borderColor),
              ),
              child: Row(
                children: [
                  const SizedBox(width: 12),
                  const Icon(Icons.search,
                      color: HomeColors.textGray, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      controller: _searchController,
                      style: GoogleFonts.roboto(
                          fontSize: 14, color: HomeColors.textPrimary),
                      onChanged: (value) {
                        setState(() {
                          _searchQuery = value.trim().toLowerCase();
                        });
                      },
                      decoration: InputDecoration(
                        hintText: 'Search by area, title or reporter…',
                        hintStyle: GoogleFonts.roboto(
                            color: HomeColors.textGray, fontSize: 14),
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.zero,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 12),
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: HomeColors.borderColor),
            ),
            child: IconButton(
              icon: const Icon(Icons.tune,
                  color: HomeColors.textSecondary, size: 22),
              onPressed: () {},
            ),
          ),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────
  // REPORT CARD
  // ─────────────────────────────────────────────

  Widget _buildReportCard(List<ReportModel> visibleReports, int index) {
    final report = visibleReports[index];
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: HomeColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: InkWell(
        onTap: () => _showCommentsBottomSheet(index),
        borderRadius: BorderRadius.circular(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                _buildAvatar(report),
                const SizedBox(width: 10),
                Expanded(child: _buildReporterInfo(report)),
                _buildStatusBadge(
                  report.status,
                  verificationStatus: report.verificationStatus,
                  combinedScore: report.combinedScore,
                  kanbanStage: report.kanbanStage,
                ),
              ],
            ),
          ),

          // Image — only show if URL exists (not empty)
          if (report.imageUrl.isNotEmpty)
            ClipRRect(
              borderRadius: BorderRadius.zero,
              child: ConstrainedBox(
                constraints: const BoxConstraints(
                  minHeight: 160,
                  maxHeight: 300,
                ),
                child: Container(
                  width: double.infinity,
                  color: const Color(0xFFF0F0F0),
                  child: CachedNetworkImage(
                    imageUrl: ApiService.imageUrl(report.imageUrl),
                    fit: BoxFit.contain,
                    placeholder: (_, __) => const SizedBox(
                      height: 200,
                      child: Center(
                        child: CircularProgressIndicator(
                            color: HomeColors.statusOrange),
                      ),
                    ),
                    errorWidget: (_, __, ___) => const SizedBox(
                      height: 120,
                      child: Center(
                        child: Icon(Icons.image_not_supported,
                            color: HomeColors.textGray, size: 36),
                      ),
                    ),
                  ),
                ),
              ),
            ),

          // Title & description
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  report.title,
                  style: GoogleFonts.roboto(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: HomeColors.textPrimary),
                ),
                const SizedBox(height: 4),
                Text(
                  report.description,
                  style: GoogleFonts.roboto(
                      fontSize: 13,
                      color: HomeColors.textSecondary,
                      height: 1.4),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),

          // Buttons
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 4, 12, 12),
            child: Wrap(
              spacing: 12,
              runSpacing: 8,
              children: [
                _buildSupportButton(index),
                _buildVerifyButton(index),
                _buildCommentButton(index),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}

  Widget _buildAvatar(ReportModel report) {
    // Color list to pick from based on name length
    final colors = [
      const Color(0xFFC85A3A),
      const Color(0xFFD4A574),
      const Color(0xFFB59B8F),
      const Color(0xFFA0826D),
      const Color(0xFF8B6F5E),
    ];
    final color = colors[report.reporterName.length % colors.length];

    if (report.reporterAvatarUrl != null &&
        report.reporterAvatarUrl!.isNotEmpty) {
      return ClipOval(
        child: CachedNetworkImage(
          imageUrl: ApiService.imageUrl(report.reporterAvatarUrl!),
          width: 40,
          height: 40,
          fit: BoxFit.cover,
          placeholder: (_, __) => _initialsCircle(report.reporterInitials, color),
          errorWidget: (_, __, ___) =>
              _initialsCircle(report.reporterInitials, color),
        ),
      );
    }
    return _initialsCircle(report.reporterInitials, color);
  }

  Widget _initialsCircle(String initials, Color color) {
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
      child: Center(
        child: Text(
          initials,
          style: GoogleFonts.roboto(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 14),
        ),
      ),
    );
  }

  Widget _buildReporterInfo(ReportModel report) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Flexible(
              child: Text(
                report.reporterName,
                style: GoogleFonts.roboto(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                    color: HomeColors.textPrimary),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            Text(
              ' · ${report.timeAgo}',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              softWrap: false,
              style: GoogleFonts.roboto(
                  fontSize: 12, color: HomeColors.textGray),
            ),
          ],
        ),
        const SizedBox(height: 2),
        Row(
          children: [
            const Icon(Icons.location_on,
                size: 12, color: HomeColors.statusOrange),
            const SizedBox(width: 4),
            Expanded(
              child: Text(
                report.location,
                style: GoogleFonts.roboto(
                    fontSize: 11,
                    color: HomeColors.statusOrange,
                    fontWeight: FontWeight.w500),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatusBadge(
    String status, {
    String? verificationStatus,
    double? combinedScore,
    String? kanbanStage,
  }) {
    Color bgColor;
    String label;

    if (kanbanStage == 'AWAITING_FEEDBACK') {
      bgColor = const Color(0xFF7C3AED);
      label = 'CONFIRM FIX';
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
            color: bgColor, borderRadius: BorderRadius.circular(4)),
        child: Text(
          label,
          style: GoogleFonts.roboto(
              fontSize: 10,
              color: Colors.white,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.5),
        ),
      );
    }

    // Use Report.status for other lifecycle UI.
    switch (status) {
      case 'VERIFIED':
        bgColor = HomeColors.statusGreen;
        label = 'VERIFIED';
        break;
      case 'REVIEW_NEEDED':
        bgColor = Colors.amber[700] ?? Colors.amber;
        label = 'REVIEW NEEDED';
        break;
      case 'PENDING':
      case 'REPORTED':
        bgColor = HomeColors.statusRed;
        label = 'PENDING';
        break;
      case 'IN_PROGRESS':
        bgColor = Colors.amber[700] ?? Colors.amber;
        label = 'IN PROGRESS';
        break;
      case 'RESOLVED':
        bgColor = HomeColors.statusGreen;
        label = 'RESOLVED';
        break;
      default:
        bgColor = HomeColors.textGray;
        label = status;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration:
          BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(4)),
      child: Text(
        label,
        style: GoogleFonts.roboto(
            fontSize: 10,
            color: Colors.white,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.5),
      ),
    );
  }

  Widget _buildSupportButton(int index) {
    final report = _reports[index];
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => _onSupportTap(index),
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: report.hasSupported
                ? HomeColors.statusOrange
                : HomeColors.statusOrange.withOpacity(0.1),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: report.hasSupported
                  ? HomeColors.statusOrange
                  : HomeColors.statusOrange.withOpacity(0.3),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                report.hasSupported
                    ? Icons.thumb_up
                    : Icons.thumb_up_outlined,
                size: 16,
                color: report.hasSupported
                    ? Colors.white
                    : HomeColors.statusOrange,
              ),
              const SizedBox(width: 6),
              Text(
                'Support (${report.supportCount})',
                style: GoogleFonts.roboto(
                  fontSize: 13,
                  color: report.hasSupported
                      ? Colors.white
                      : HomeColors.statusOrange,
                  fontWeight: FontWeight.w600,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                softWrap: false,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildVerifyButton(int index) {
    final report = _reports[index];
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => _onVerifyTap(index),
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: report.hasVerified
                ? HomeColors.statusGreenLight
                : Colors.transparent,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: report.hasVerified
                  ? HomeColors.statusGreen
                  : HomeColors.borderColor,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                report.hasVerified
                    ? Icons.verified
                    : Icons.verified_outlined,
                size: 16,
                color: report.hasVerified
                    ? HomeColors.statusGreen
                    : HomeColors.textSecondary,
              ),
              const SizedBox(width: 6),
              Text(
                'Verify (${report.verifyCount})',
                style: GoogleFonts.roboto(
                  fontSize: 13,
                  color: report.hasVerified
                      ? HomeColors.statusGreen
                      : HomeColors.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                softWrap: false,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCommentButton(int index) {
    final report = _reports[index];
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => _showCommentsBottomSheet(index),
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: HomeColors.borderColor),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.chat_bubble_outline,
                  size: 16, color: HomeColors.textSecondary),
              const SizedBox(width: 6),
              Text(
                '${report.commentCount}',
                style: GoogleFonts.roboto(
                  fontSize: 13,
                  color: HomeColors.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _showCommentsBottomSheet(int index) async {
    final report = _reports[index];
    final TextEditingController commentController = TextEditingController();
    List<CommentModel> comments = [];
    bool loadingComments = true;
    bool submitting = false;

    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setSheetState) {
            // Load comments on first build
            if (loadingComments) {
              ApiService.getReportComments(report.id).then((result) {
                if (!mounted) return;
                setSheetState(() {
                  loadingComments = false;
                  if (result['success'] == true) {
                    final raw = result['data']['comments'] as List<dynamic>;
                    comments = raw
                        .map((c) => CommentModel.fromJson(c as Map<String, dynamic>))
                        .toList();
                  }
                });
              });
            }

            return DraggableScrollableSheet(
              initialChildSize: 0.6,
              minChildSize: 0.4,
              maxChildSize: 0.92,
              expand: false,
              builder: (_, scrollController) {
                return Container(
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
                  ),
                  child: Column(
                    children: [
                      // Handle
                      Center(
                        child: Container(
                          margin: const EdgeInsets.only(top: 12, bottom: 8),
                          width: 40,
                          height: 4,
                          decoration: BoxDecoration(
                            color: HomeColors.borderColor,
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                      ),
                      // Title
                      Padding(
                        padding: const EdgeInsets.fromLTRB(16, 4, 16, 12),
                        child: Row(
                          children: [
                            Text(
                              'Comments (${comments.length})',
                              style: GoogleFonts.roboto(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: HomeColors.textPrimary,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Divider(height: 1),
                      // Comment list
                      Expanded(
                        child: loadingComments
                            ? const Center(
                                child: CircularProgressIndicator(
                                    color: HomeColors.statusOrange),
                              )
                            : comments.isEmpty
                                ? Center(
                                    child: Column(
                                      mainAxisAlignment: MainAxisAlignment.center,
                                      children: [
                                        const Icon(Icons.chat_bubble_outline,
                                            size: 48,
                                            color: HomeColors.textGray),
                                        const SizedBox(height: 12),
                                        Text('No comments yet',
                                            style: GoogleFonts.roboto(
                                                color: HomeColors.textSecondary,
                                                fontSize: 14)),
                                        Text('Be the first to comment!',
                                            style: GoogleFonts.roboto(
                                                color: HomeColors.textGray,
                                                fontSize: 12)),
                                      ],
                                    ),
                                  )
                                : ListView.separated(
                                    controller: scrollController,
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 16, vertical: 8),
                                    itemCount: comments.length,
                                    separatorBuilder: (_, __) =>
                                        const SizedBox(height: 12),
                                    itemBuilder: (_, i) =>
                                        _buildCommentTile(comments[i], () {
                                      setSheetState(() => comments.removeAt(i));
                                      // Update card count
                                      final idx = _reports
                                          .indexWhere((r) => r.id == report.id);
                                      if (idx != -1) {
                                        setState(() {
                                          final r = _reports[idx];
                                          _reports[idx] = ReportModel(
                                            id: r.id,
                                            reporterId: r.reporterId,
                                            reporterName: r.reporterName,
                                            reporterInitials: r.reporterInitials,
                                            reporterAvatarUrl: r.reporterAvatarUrl,
                                            timestamp: r.timestamp,
                                            location: r.location,
                                            locationCity: r.locationCity,
                                            issueCategory: r.issueCategory,
                                            title: r.title,
                                            description: r.description,
                                            imageUrl: r.imageUrl,
                                            views: r.views,
                                            supportCount: r.supportCount,
                                            verifyCount: r.verifyCount,
                                            commentCount:
                                                (r.commentCount - 1).clamp(0, 9999),
                                            status: r.status,
                                            kanbanStage: r.kanbanStage,
                                            combinedScore: r.combinedScore,
                                            verificationStatus: r.verificationStatus,
                                            locationLat: r.locationLat,
                                            locationLng: r.locationLng,
                                            hasSupported: r.hasSupported,
                                            hasVerified: r.hasVerified,
                                          );
                                        });
                                      }
                                    }),
                                  ),
                      ),
                      const Divider(height: 1),
                      // Input row
                      Padding(
                        padding: EdgeInsets.only(
                          left: 12,
                          right: 12,
                          top: 8,
                          bottom: MediaQuery.of(ctx).viewInsets.bottom + 12,
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: commentController,
                                maxLength: 500,
                                maxLines: 3,
                                minLines: 1,
                                decoration: InputDecoration(
                                  hintText: 'Write a comment...',
                                  hintStyle: GoogleFonts.roboto(
                                      color: HomeColors.textGray, fontSize: 14),
                                  filled: true,
                                  fillColor: HomeColors.backgroundColor,
                                  contentPadding: const EdgeInsets.symmetric(
                                      horizontal: 14, vertical: 10),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(20),
                                    borderSide: BorderSide.none,
                                  ),
                                  counterText: '',
                                ),
                                style: GoogleFonts.roboto(
                                    fontSize: 14,
                                    color: HomeColors.textPrimary),
                              ),
                            ),
                            const SizedBox(width: 8),
                            submitting
                                ? const SizedBox(
                                    width: 40,
                                    height: 40,
                                    child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        color: HomeColors.statusOrange),
                                  )
                                : IconButton(
                                    onPressed: () async {
                                      final text =
                                          commentController.text.trim();
                                      if (text.isEmpty) return;
                                      
                                      setSheetState(() => submitting = true);

                                      final result = await ApiService.createComment(
                                          report.id, text);
                                      
                                      if (!mounted) return;

                                      try {
                                        if (result['success'] == true) {
                                          final newComment = CommentModel.fromJson(
                                              result['data']['comment']
                                                  as Map<String, dynamic>);
                                          
                                          commentController.clear();
                                          
                                          setSheetState(() {
                                            comments.add(newComment);
                                            submitting = false;
                                          });

                                          final idx = _reports.indexWhere(
                                              (r) => r.id == report.id);
                                          if (idx != -1) {
                                            setState(() {
                                              final r = _reports[idx];
                                              _reports[idx] = ReportModel(
                                                id: r.id,
                                                reporterId: r.reporterId,
                                                reporterName: r.reporterName,
                                                reporterInitials: r.reporterInitials,
                                                reporterAvatarUrl: r.reporterAvatarUrl,
                                                timestamp: r.timestamp,
                                                location: r.location,
                                                locationCity: r.locationCity,
                                                issueCategory: r.issueCategory,
                                                title: r.title,
                                                description: r.description,
                                                imageUrl: r.imageUrl,
                                                views: r.views,
                                                supportCount: r.supportCount,
                                                verifyCount: r.verifyCount,
                                                commentCount: r.commentCount + 1,
                                                status: r.status,
                                                kanbanStage: r.kanbanStage,
                                                combinedScore: r.combinedScore,
                                                verificationStatus:
                                                    r.verificationStatus,
                                                locationLat: r.locationLat,
                                                locationLng: r.locationLng,
                                                hasSupported: r.hasSupported,
                                                hasVerified: r.hasVerified,
                                              );
                                            });
                                          }
                                        } else {
                                          setSheetState(() => submitting = false);
                                        }
                                      } catch (e) {
                                        // Sheet probably closed, ignore gracefully
                                      }
                                    },
                                    icon: const Icon(Icons.send_rounded,
                                        color: HomeColors.statusOrange),
                                  ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            );
          },
        );
      },
    ).then((_) => commentController.dispose());
  }

  Widget _buildCommentTile(CommentModel comment, VoidCallback onDeleted) {
    final colors = [
      const Color(0xFFC85A3A),
      const Color(0xFFD4A574),
      const Color(0xFFB59B8F),
      const Color(0xFFA0826D),
      const Color(0xFF8B6F5E),
    ];
    final color = colors[comment.userName.length % colors.length];

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Avatar
        comment.userAvatarUrl != null && comment.userAvatarUrl!.isNotEmpty
            ? ClipOval(
                child: CachedNetworkImage(
                  imageUrl: ApiService.imageUrl(comment.userAvatarUrl!),
                  width: 34,
                  height: 34,
                  fit: BoxFit.cover,
                  errorWidget: (_, __, ___) =>
                      _initialsCircle(comment.userInitials, color),
                ),
              )
            : Container(
                width: 34,
                height: 34,
                decoration: BoxDecoration(color: color, shape: BoxShape.circle),
                child: Center(
                  child: Text(
                    comment.userInitials,
                    style: GoogleFonts.roboto(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 12),
                  ),
                ),
              ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    comment.userName,
                    style: GoogleFonts.roboto(
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                        color: HomeColors.textPrimary),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    comment.timeAgo,
                    style: GoogleFonts.roboto(
                        fontSize: 11, color: HomeColors.textGray),
                  ),
                  if (comment.isOwnComment) ...[
                    const Spacer(),
                    GestureDetector(
                      onTap: () async {
                        final result =
                            await ApiService.deleteComment(comment.id);
                        if (result['success'] == true) onDeleted();
                      },
                      child: const Icon(Icons.delete_outline,
                          size: 16, color: HomeColors.textGray),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 3),
              Text(
                comment.text,
                style: GoogleFonts.roboto(
                    fontSize: 13,
                    color: HomeColors.textPrimary,
                    height: 1.4),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // ─────────────────────────────────────────────
  // NOTIFICATIONS
  // ─────────────────────────────────────────────

}
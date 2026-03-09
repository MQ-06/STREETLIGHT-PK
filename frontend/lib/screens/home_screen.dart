// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:geolocator/geolocator.dart';
import '../models/comment_model.dart';
import '../models/report_model.dart';
import '../models/verification_model.dart';
import '../services/api_service.dart';
import 'report_issue_screen.dart';
import 'profile_screen.dart';

class HomeColors {
  static const backgroundColor = Color(0xFFFFF8E7);
  static const cardBackground = Color(0xFFFFFFFF);
  static const statusOrange = Color(0xFFC85A3A);
  static const statusBrown = Color(0xFF5C4033);
  static const textPrimary = Color(0xFF000000);
  static const textSecondary = Color(0xFF666666);
  static const textGray = Color(0xFFAAAAAA);
  static const borderColor = Color(0xFFEEEEEE);
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  final TextEditingController _searchController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  List<ReportModel> _reports = [];
  bool _isLoading = true;
  bool _isLoadingMore = false;
  String? _errorMessage;
  int _currentSkip = 0;
  static const int _pageSize = 20;
  bool _hasMore = true;

  // ── Community verification notifications ──────────────────────────────────
  List<VerificationRequestModel> _pendingVerifications = [];
  double? _userLat;
  double? _userLng;

  @override
  void initState() {
    super.initState();
    _loadFeed(refresh: true);
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // ─────────────────────────────────────────────
  // DATA
  // ─────────────────────────────────────────────

  Future<void> _loadFeed({bool refresh = false}) async {
    if (refresh) {
      setState(() {
        _isLoading = true;
        _currentSkip = 0;
        _hasMore = true;
        _errorMessage = null;
        _reports = [];
      });
      // Fetch nearby verification requests in parallel with the feed
      _fetchPendingVerifications();
    }

    final result = await ApiService.getReportsFeed(
      skip: refresh ? 0 : _currentSkip,
      limit: _pageSize,
    );

    if (!mounted) return;

    if (result['success'] == true) {
      final raw = result['data']['reports'] as List<dynamic>;
      final newReports = raw.map((r) => ReportModel.fromJson(r)).toList();
      setState(() {
        _reports.addAll(newReports);
        _currentSkip = _reports.length;
        _hasMore = newReports.length == _pageSize;
        _isLoading = false;
        _isLoadingMore = false;
      });
    } else {
      // Session expired → kick to login
      if (result['code'] == 401) {
        await ApiService.logout();
        if (mounted) Navigator.pushReplacementNamed(context, '/login_form');
        return;
      }
      setState(() {
        _errorMessage = result['error'];
        _isLoading = false;
        _isLoadingMore = false;
      });
    }
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
            _scrollController.position.maxScrollExtent - 200 &&
        !_isLoadingMore &&
        _hasMore) {
      setState(() => _isLoadingMore = true);
      _loadFeed();
    }
  }

  // ─────────────────────────────────────────────
  // PENDING VERIFICATIONS (bell badge)
  // ─────────────────────────────────────────────

  Future<void> _fetchPendingVerifications() async {
    try {
      // Use last-known position — fast, no blocking permission dialog
      Position? position;
      try {
        final permission = await Geolocator.checkPermission();
        if (permission == LocationPermission.whileInUse ||
            permission == LocationPermission.always) {
          position = await Geolocator.getLastKnownPosition();
        }
      } catch (_) {}

      // Lahore city-centre fallback if GPS unavailable
      final lat = position?.latitude ?? 31.5204;
      final lng = position?.longitude ?? 74.3587;

      if (mounted) setState(() { _userLat = lat; _userLng = lng; });

      final result = await ApiService.getPendingVerifications(lat, lng);
      if (!mounted) return;

      if (result['success'] == true) {
        final raw = result['data']['requests'] as List<dynamic>;
        setState(() {
          _pendingVerifications = raw
              .map((r) => VerificationRequestModel.fromJson(
                    r as Map<String, dynamic>))
              .toList();
        });
      }
    } catch (e) {
      debugPrint('HomeScreen — pending verifications fetch error: $e');
    }
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
      bottomNavigationBar: _buildBottomNavBar(),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const ReportIssueScreen()),
          );
          if (result == true) _loadFeed(refresh: true);
        },
        backgroundColor: HomeColors.statusOrange,
        child: const Icon(Icons.add, color: Colors.white, size: 28),
      ),
    );
  }

  Widget _buildBody() {
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
    if (_reports.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.inbox_outlined,
                size: 64, color: HomeColors.textGray),
            const SizedBox(height: 16),
            Text(
              'No reports yet.\nBe the first to report an issue!',
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
        itemCount: _reports.length + (_isLoadingMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == _reports.length) {
            return const Padding(
              padding: EdgeInsets.all(16),
              child: Center(
                child:
                    CircularProgressIndicator(color: HomeColors.statusOrange),
              ),
            );
          }
          return _buildReportCard(index);
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
            builder: (context) => Stack(
              clipBehavior: Clip.none,
              children: [
                IconButton(
                  icon: const Icon(Icons.notifications_outlined,
                      color: HomeColors.textSecondary),
                  onPressed: () => _showNotificationDropdown(context),
                ),
                if (_pendingVerifications.isNotEmpty)
                  Positioned(
                    right: 6,
                    top: 6,
                    child: Container(
                      width: 18,
                      height: 18,
                      decoration: const BoxDecoration(
                        color: HomeColors.statusOrange,
                        shape: BoxShape.circle,
                      ),
                      child: Center(
                        child: Text(
                          '${_pendingVerifications.length}',
                          style: GoogleFonts.roboto(
                            fontSize: 10,
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
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
                      decoration: InputDecoration(
                        hintText: 'Search community reports...',
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

  Widget _buildReportCard(int index) {
    final report = _reports[index];
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
                _buildStatusBadge(report.status),
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
            child: Row(
              children: [
                _buildSupportButton(index),
                const SizedBox(width: 12),
                _buildVerifyButton(index),
                const SizedBox(width: 12),
                _buildCommentButton(index),
              ],
            ),
          ),
        ],
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

  Widget _buildStatusBadge(String status) {
    if (status == 'REPORTED') {
      return Text(
        'REPORTED',
        style: GoogleFonts.roboto(
            fontSize: 10,
            color: HomeColors.textGray,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.5),
      );
    }

    Color bgColor;
    String label;
    switch (status) {
      case 'VERIFIED':
        bgColor = HomeColors.statusOrange;
        label = 'VERIFIED';
        break;
      case 'IN_PROGRESS':
        bgColor = HomeColors.statusBrown;
        label = 'IN PROGRESS';
        break;
      case 'RESOLVED':
        bgColor = Colors.green;
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
                ? HomeColors.statusBrown
                : Colors.transparent,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: report.hasVerified
                  ? HomeColors.statusBrown
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
                    ? Colors.white
                    : HomeColors.textSecondary,
              ),
              const SizedBox(width: 6),
              Text(
                'Verify (${report.verifyCount})',
                style: GoogleFonts.roboto(
                  fontSize: 13,
                  color: report.hasVerified
                      ? Colors.white
                      : HomeColors.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
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

                                      final result =
                                          await ApiService.createComment(
                                              report.id, text);
                                      if (!mounted) return;

                                      if (result['success'] == true) {
                                        final newComment =
                                            CommentModel.fromJson(result['data']
                                                ['comment'] as Map<String, dynamic>);
                                        commentController.clear();
                                        setSheetState(() {
                                          comments.add(newComment);
                                          submitting = false;
                                        });
                                        // Update card count
                                        final idx = _reports.indexWhere(
                                            (r) => r.id == report.id);
                                        if (idx != -1) {
                                          setState(() {
                                            final r = _reports[idx];
                                            _reports[idx] = ReportModel(
                                              id: r.id,
                                              reporterId: r.reporterId,
                                              reporterName: r.reporterName,
                                              reporterInitials:
                                                  r.reporterInitials,
                                              reporterAvatarUrl:
                                                  r.reporterAvatarUrl,
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
                                              hasSupported: r.hasSupported,
                                              hasVerified: r.hasVerified,
                                            );
                                          });
                                        }
                                      } else {
                                        setSheetState(() => submitting = false);
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
    );
    commentController.dispose();
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

  Future<void> _showNotificationDropdown(BuildContext context) async {
    final RenderBox button = context.findRenderObject() as RenderBox;
    final RenderBox overlay =
        Overlay.of(context).context.findRenderObject() as RenderBox;
    final Offset offset =
        button.localToGlobal(Offset(0, button.size.height), ancestor: overlay);

    // ── Empty state ──────────────────────────────────────────────────────────
    if (_pendingVerifications.isEmpty) {
      showMenu(
        context: context,
        position: RelativeRect.fromLTRB(
            offset.dx - 150, offset.dy,
            offset.dx + button.size.width, offset.dy + 100),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        items: [
          PopupMenuItem(
            enabled: false,
            child: Container(
              padding:
                  const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
              child: Column(
                children: [
                  const Icon(Icons.notifications_off_outlined,
                      size: 40, color: HomeColors.textGray),
                  const SizedBox(height: 8),
                  Text('No Notifications',
                      style: GoogleFonts.roboto(
                          fontSize: 14,
                          color: HomeColors.textSecondary,
                          fontWeight: FontWeight.w500)),
                  const SizedBox(height: 4),
                  Text("You're all caught up!",
                      style: GoogleFonts.roboto(
                          fontSize: 12, color: HomeColors.textGray)),
                ],
              ),
            ),
          ),
        ],
      );
      return;
    }

    // ── Populated state ──────────────────────────────────────────────────────
    final tapped = await showMenu<int>(
      context: context,
      position: RelativeRect.fromLTRB(
          offset.dx - 220, offset.dy,
          offset.dx + button.size.width, offset.dy + 100),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      items: _pendingVerifications
          .map((req) => PopupMenuItem<int>(
                value: req.requestId,
                child: _buildNotificationItem(req),
              ))
          .toList(),
    );

    if (tapped != null && mounted) {
      await Navigator.pushNamed(context, '/verification');
      _loadFeed(refresh: true);
    }
  }

  Widget _buildNotificationItem(VerificationRequestModel req) {
    final distLabel = req.distanceM >= 1000
        ? '${(req.distanceM / 1000).toStringAsFixed(1)} km away'
        : '${req.distanceM.toInt()} m away';

    return SizedBox(
      width: 240,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: HomeColors.statusOrange,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  req.title,
                  style: GoogleFonts.roboto(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: HomeColors.textPrimary,
                  ),
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 2),
          Padding(
            padding: const EdgeInsets.only(left: 16),
            child: Text(
              'Verification Needed · $distLabel',
              style: GoogleFonts.roboto(
                fontSize: 11,
                color: HomeColors.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────
  // BOTTOM NAV
  // ─────────────────────────────────────────────

  Widget _buildBottomNavBar() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, -2)),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(0, Icons.home, 'Home'),
              _buildNavItem(1, Icons.explore, 'Explore'),
              _buildNavItem(2, Icons.person_outline, 'Profile'),
              _buildNavItem(3, Icons.warning_amber_rounded, 'Issues'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(int index, IconData icon, String label) {
    bool isActive = _currentIndex == index;
    return InkWell(
      onTap: () {
        if (index == 1) {
          Navigator.pushReplacementNamed(context, '/explore');
        } else if (index == 2) {
          Navigator.push(context,
              MaterialPageRoute(builder: (_) => const ProfileScreen()));
        } else if (index == 3) {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const ReportIssueScreen()),
          ).then((result) {
            if (result == true) _loadFeed(refresh: true);
          });
        } else {
          setState(() => _currentIndex = index);
        }
      },
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon,
                size: 24,
                color:
                    isActive ? HomeColors.statusOrange : HomeColors.textGray),
            const SizedBox(height: 4),
            Text(label,
                style: GoogleFonts.roboto(
                    fontSize: 11,
                    color: isActive
                        ? HomeColors.statusOrange
                        : HomeColors.textGray,
                    fontWeight: isActive
                        ? FontWeight.w600
                        : FontWeight.normal)),
          ],
        ),
      ),
    );
  }
}
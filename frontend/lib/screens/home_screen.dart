// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/report_model.dart';
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
            builder: (context) => IconButton(
              icon: const Icon(Icons.notifications_outlined,
                  color: HomeColors.textSecondary),
              onPressed: () => _showNotificationDropdown(context),
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
            CachedNetworkImage(
              imageUrl: ApiService.imageUrl(report.imageUrl),
              height: 180,
              width: double.infinity,
              fit: BoxFit.cover,
              placeholder: (_, __) => Container(
                height: 180,
                color: HomeColors.borderColor,
                child: const Center(
                  child: CircularProgressIndicator(
                      color: HomeColors.statusOrange),
                ),
              ),
              errorWidget: (_, __, ___) => Container(
                height: 100,
                color: HomeColors.borderColor,
                child: const Center(
                  child: Icon(Icons.image_not_supported,
                      color: HomeColors.textGray, size: 36),
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

  // ─────────────────────────────────────────────
  // NOTIFICATIONS
  // ─────────────────────────────────────────────

  void _showNotificationDropdown(BuildContext context) {
    final RenderBox button = context.findRenderObject() as RenderBox;
    final RenderBox overlay =
        Overlay.of(context).context.findRenderObject() as RenderBox;
    final Offset offset =
        button.localToGlobal(Offset(0, button.size.height), ancestor: overlay);
    showMenu(
      context: context,
      position: RelativeRect.fromLTRB(
          offset.dx - 150, offset.dy, offset.dx + button.size.width, offset.dy + 100),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      items: [
        PopupMenuItem(
          enabled: false,
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
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
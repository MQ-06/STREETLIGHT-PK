//screens/profile_screen.dart
import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import '../models/user_profile.dart';
import '../models/civic_report.dart';
import '../services/user_session.dart';
import 'report_issue_screen.dart';
import '../services/api_service.dart';
import '../widgets/app_toast.dart';

/// Color palette for Profile screen
class ProfileColors {
  static const backgroundColor = Color(0xFFFFF8E7);
  static const cardBackground = Color(0xFFFFFFFF);
  static const profileRing = Color(0xFFC85A3A);
  static const primaryRust = Color(0xFFA0522D);
  static const accentOrange = Color(0xFFC85A3A);
  static const textPrimary = Color(0xFF3E2723);
  static const textSecondary = Color(0xFF666666);
  static const textTan = Color(0xFF8B7355);
  static const statCardBg = Color(0xFFF5E6E6);
  static const statusYellow = Color(0xFFFFF3CD);
  static const priorityHigh = Color(0xFFC85A3A);
  static const borderLight = Color(0xFFEEEEEE);
  static const successGreen = Color(0xFF4CAF50);
}

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  // User data from session
  String _userName = 'Guest User';
  String _userLocation = 'Fetching location...';
  String? _profileImagePath;
  int _totalReported = 0;
  int _totalResolved = 0;
  int _impactScore = 0;
  double _impactPercentage = 0.0;

  // User reports (Pakistan-based sample data)
  late List<CivicReport> userReports;

  // Filter state
  ReportFilterTab _selectedTab = ReportFilterTab.MY_REPORTS;
  String _selectedCategory = 'ALL';

  // UI state
  int _currentNavIndex = 2; // Profile tab
  bool _isLoading = true;
  bool _isLoadingLocation = false;

  final ImagePicker _imagePicker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _initializeProfile();
  }

  Future<void> _initializeProfile() async {
    // Load user data from session
    _userName = await UserSession.getUserName();
    _userLocation = await UserSession.getUserLocation();
    _profileImagePath = await UserSession.getProfileImagePath();
    // Initialize Pakistan-based sample reports

    // userReports already fetch ho chuki hai ApiService.getMyReports() se upar
    final myReports = await ApiService.getMyReports();
    if (myReports['success'] == true) {
      final reports = myReports['data']['reports'] as List<dynamic>;
      _totalReported = reports.length;
      _totalResolved = reports.where((r) => r['status'] == 'RESOLVED').length;
      _impactPercentage = _totalReported > 0
          ? (_totalResolved / _totalReported) * 100
          : 0.0;
      _impactScore = _impactPercentage.toInt() * 10;

      // Real reports from backend
      userReports = reports
          .map(
            (r) => CivicReport(
              id: r['id'].toString(),
              reporterId: r['reporter_id'].toString(),
              reporterName: r['reporter_name'] ?? '',
              reporterInitials: r['reporter_initials'] ?? '',
              reporterAvatar: '#C85A3A',
              timestamp: DateTime.parse(r['timestamp']),
              location: r['location'] ?? '',
              issueCategory: r['issue_category'] ?? '',
              title: r['title'] ?? '',
              description: r['description'] ?? '',
              imageUrl: r['image_url'] ?? '',
              views: r['views'] ?? 0,
              verificationCount: r['verify_count'] ?? 0,
              supportCount: r['support_count'] ?? 0,
              verifications: [],
            ),
          )
          .toList();
    } else {
      userReports = [];
    }
    setState(() => _isLoading = false);
  }

  String _getInitials(String name) {
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    } else if (parts.isNotEmpty && parts[0].isNotEmpty) {
      return parts[0][0].toUpperCase();
    }
    return 'U';
  }

  Future<void> _fetchCurrentLocation() async {
    setState(() => _isLoadingLocation = true);

    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          setState(() {
            _userLocation = 'Location permission denied';
            _isLoadingLocation = false;
          });
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        setState(() {
          _userLocation = 'Opening app settings...';
          _isLoadingLocation = false;
        });
        await openAppSettings();
        return;
      }

      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        setState(() {
          _userLocation = 'Opening location settings...';
          _isLoadingLocation = false;
        });
        await Geolocator.openLocationSettings();
        return;
      }

      Position position;
      try {
        position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.medium,
          timeLimit: const Duration(seconds: 15),
        );
      } on TimeoutException {
        setState(() {
          _userLocation = 'Timed out. Try outdoors or near a window.';
          _isLoadingLocation = false;
        });
        return;
      } catch (e) {
        setState(() {
          _userLocation = 'Location error: $e';
          _isLoadingLocation = false;
        });
        return;
      }

      try {
        final placemarks = await placemarkFromCoordinates(
          position.latitude,
          position.longitude,
        );

        if (placemarks.isNotEmpty) {
          final place = placemarks.first;
          final location =
              '${place.subLocality ?? place.locality ?? ''}, ${place.locality ?? place.administrativeArea ?? 'Pakistan'}';
          setState(() => _userLocation = location);
          await UserSession.setUserLocation(location);
        }
      } catch (e) {
        setState(
          () => _userLocation =
              'Lat: ${position.latitude.toStringAsFixed(4)}, Lng: ${position.longitude.toStringAsFixed(4)}',
        );
      }
    } catch (e) {
      setState(() => _userLocation = 'Could not fetch location');
    } finally {
      setState(() => _isLoadingLocation = false);
    }
  }

  Future<void> _uploadProfileImage() async {
    try {
      // Try picker first - image_picker handles permissions; permission_handler
      // can incorrectly report "denied" on some devices when permission is granted.
      final pickedFile = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85,
        maxWidth: 512,
        maxHeight: 512,
      );

      if (pickedFile != null) {
        final localPath = pickedFile.path;
        await UserSession.setProfileImagePath(localPath);

        setState(() => _profileImagePath = localPath);

        showAppToast(context,
            message: 'Profile photo updated',
            isError: false,
            duration: const Duration(seconds: 2));
      }
    } catch (e) {
      final err = e.toString().toLowerCase();
      if (err.contains('permission') || err.contains('denied') ||
          err.contains('access') || err.contains('photo')) {
        _showGalleryPermissionDialog();
      } else {
        showAppToast(context,
            message: 'Error uploading photo: $e', isError: true);
      }
    }
  }

  void _showGalleryPermissionDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Gallery Access Required',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w600),
        ),
        content: Text(
          'Gallery permission was denied. Open settings to enable it?',
          style: GoogleFonts.roboto(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel', style: TextStyle(color: ProfileColors.textSecondary)),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              openAppSettings();
            },
            child: Text(
              'Open Settings',
              style: TextStyle(color: ProfileColors.accentOrange),
            ),
          ),
        ],
      ),
    );
  }

  List<CivicReport> _getFilteredReports() {
    List<CivicReport> filtered = List.from(userReports);

    switch (_selectedTab) {
      case ReportFilterTab.MY_REPORTS:
        filtered = filtered.where((r) => r.status != 'RESOLVED').toList();
        break;
      case ReportFilterTab.RESOLVED:
        filtered = filtered.where((r) => r.status == 'RESOLVED').toList();
        break;
      case ReportFilterTab.IMPACT:
        // Impact tab shows stats, not reports
        return [];
    }

    if (_selectedCategory != 'ALL') {
      filtered = filtered
          .where((r) => r.issueCategory == _selectedCategory)
          .toList();
    }

    return filtered;
  }

  String _formatNumber(int number) {
    if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}k';
    }
    return number.toString();
  }

  /// Refresh profile data (called when returning from report submission)
  Future<void> _refreshProfileData() async {
    final myReports = await ApiService.getMyReports();
    if (myReports['success'] == true) {
      final reports = myReports['data']['reports'] as List<dynamic>;
      setState(() {
        _totalReported = reports.length;
        _totalResolved = reports.where((r) => r['status'] == 'RESOLVED').length;
        _impactPercentage = _totalReported > 0
            ? (_totalResolved / _totalReported) * 100
            : 0.0;
        _impactScore = _impactPercentage.toInt() * 10;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: ProfileColors.backgroundColor,
        body: const Center(
          child: CircularProgressIndicator(color: ProfileColors.accentOrange),
        ),
      );
    }

    return Scaffold(
      backgroundColor: ProfileColors.backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    _buildHeader(),
                    _buildProfileCard(),
                    _buildImpactScoreCard(),
                    _buildStatsCards(),
                    _buildTabsSection(),
                    if (_selectedTab != ReportFilterTab.IMPACT)
                      _buildCategoryFilter(),
                    if (_selectedTab == ReportFilterTab.IMPACT)
                      _buildImpactStats()
                    else
                      _buildReportsList(),
                    const SizedBox(height: 80),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: _buildFAB(),
      bottomNavigationBar: _buildBottomNavBar(),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Text(
        'Profile & Impact',
        style: GoogleFonts.poppins(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: ProfileColors.primaryRust,
        ),
      ),
    );
  }

  Widget _buildProfileCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        children: [
          GestureDetector(
            onTap: _uploadProfileImage,
            child: Stack(
              children: [
                Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: ProfileColors.profileRing,
                      width: 4,
                    ),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(60),
                    child:
                        _profileImagePath != null &&
                            File(_profileImagePath!).existsSync()
                        ? Image.file(
                            File(_profileImagePath!),
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => _buildDefaultAvatar(),
                          )
                        : _buildDefaultAvatar(),
                  ),
                ),
                Positioned(
                  bottom: 0,
                  right: 0,
                  child: Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: ProfileColors.accentOrange,
                      border: Border.all(color: Colors.white, width: 2),
                    ),
                    child: const Icon(
                      Icons.edit,
                      color: Colors.white,
                      size: 18,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Text(
            _userName,
            style: GoogleFonts.poppins(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: ProfileColors.textPrimary,
            ),
          ),
          const SizedBox(height: 4),
          GestureDetector(
            onTap: _isLoadingLocation ? null : _fetchCurrentLocation,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  _isLoadingLocation ? Icons.sync : Icons.location_on,
                  size: 16,
                  color: ProfileColors.accentOrange,
                ),
                const SizedBox(width: 4),
                Text(
                  _isLoadingLocation ? 'Fetching...' : _userLocation,
                  style: GoogleFonts.roboto(
                    fontSize: 14,
                    color: ProfileColors.accentOrange,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildDefaultAvatar() {
    return Container(
      color: ProfileColors.statCardBg,
      child: Center(
        child: Text(
          _getInitials(_userName),
          style: GoogleFonts.poppins(
            fontSize: 40,
            fontWeight: FontWeight.bold,
            color: ProfileColors.primaryRust,
          ),
        ),
      ),
    );
  }

  Widget _buildImpactScoreCard() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: ProfileColors.statCardBg,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'IMPACT SCORE',
                style: GoogleFonts.roboto(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: ProfileColors.textTan,
                  letterSpacing: 1,
                ),
              ),
              if (_impactPercentage > 0)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: ProfileColors.successGreen.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '+${_impactPercentage.toStringAsFixed(1)}%',
                    style: GoogleFonts.roboto(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: ProfileColors.successGreen,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                _impactScore.toString(),
                style: GoogleFonts.poppins(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  color: ProfileColors.primaryRust,
                  height: 1,
                ),
              ),
              Padding(
                padding: const EdgeInsets.only(bottom: 8, left: 4),
                child: Text(
                  '/1000',
                  style: GoogleFonts.roboto(
                    fontSize: 16,
                    color: ProfileColors.textSecondary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: _impactScore / 1000,
              minHeight: 8,
              backgroundColor: ProfileColors.borderLight,
              valueColor: AlwaysStoppedAnimation<Color>(
                ProfileColors.accentOrange,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsCards() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: _buildStatCard(
              icon: Icons.report_problem_outlined,
              label: 'REPORTED',
              value: _totalReported.toString(),
              progress: 1.0,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildStatCard(
              icon: Icons.check_circle_outline,
              label: 'RESOLVED',
              value: _totalResolved.toString(),
              progress: _totalReported > 0
                  ? _totalResolved / _totalReported
                  : 0,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String label,
    required String value,
    required double progress,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: ProfileColors.borderLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: ProfileColors.accentOrange),
              const SizedBox(width: 6),
              Text(
                label,
                style: GoogleFonts.roboto(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: ProfileColors.accentOrange,
                  letterSpacing: 0.5,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: GoogleFonts.poppins(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: ProfileColors.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(2),
            child: LinearProgressIndicator(
              value: progress.clamp(0, 1),
              minHeight: 4,
              backgroundColor: ProfileColors.borderLight,
              valueColor: AlwaysStoppedAnimation<Color>(
                ProfileColors.accentOrange,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabsSection() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Row(
        children: [
          _buildTab('MY REPORTS', ReportFilterTab.MY_REPORTS),
          const SizedBox(width: 24),
          _buildTab('RESOLVED', ReportFilterTab.RESOLVED),
          const SizedBox(width: 24),
          _buildTab('IMPACT', ReportFilterTab.IMPACT),
        ],
      ),
    );
  }

  Widget _buildTab(String label, ReportFilterTab tab) {
    final isSelected = _selectedTab == tab;
    return GestureDetector(
      onTap: () => setState(() => _selectedTab = tab),
      child: Column(
        children: [
          Text(
            label,
            style: GoogleFonts.roboto(
              fontSize: 13,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              color: isSelected
                  ? ProfileColors.primaryRust
                  : ProfileColors.textSecondary,
            ),
          ),
          const SizedBox(height: 4),
          Container(
            height: 2,
            width: label.length * 7.0,
            color: isSelected ? ProfileColors.accentOrange : Colors.transparent,
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryFilter() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: [
          _buildCategoryChip('All', 'ALL'),
          const SizedBox(width: 8),
          _buildCategoryChip('Pothole', 'POTHOLE'),
          const SizedBox(width: 8),
          _buildCategoryChip('Trash', 'TRASH'),
        ],
      ),
    );
  }

  Widget _buildCategoryChip(String label, String value) {
    final isSelected = _selectedCategory == value;
    return GestureDetector(
      onTap: () => setState(() => _selectedCategory = value),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? ProfileColors.accentOrange : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected
                ? ProfileColors.accentOrange
                : ProfileColors.borderLight,
          ),
        ),
        child: Text(
          label,
          style: GoogleFonts.roboto(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: isSelected ? Colors.white : ProfileColors.textSecondary,
          ),
        ),
      ),
    );
  }

  Widget _buildImpactStats() {
    final totalIssues = _totalReported;
    final resolvedIssues = _totalResolved;
    final pendingIssues = totalIssues - resolvedIssues;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: ProfileColors.borderLight),
      ),
      child: Column(
        children: [
          Text(
            'YOUR IMPACT',
            style: GoogleFonts.roboto(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: ProfileColors.textTan,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 24),
          // Large percentage display
          Container(
            width: 160,
            height: 160,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: ProfileColors.statCardBg,
              border: Border.all(color: ProfileColors.accentOrange, width: 6),
            ),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    '${_impactPercentage.toStringAsFixed(1)}%',
                    style: GoogleFonts.poppins(
                      fontSize: 36,
                      fontWeight: FontWeight.bold,
                      color: ProfileColors.primaryRust,
                    ),
                  ),
                  Text(
                    'Impact Rate',
                    style: GoogleFonts.roboto(
                      fontSize: 12,
                      color: ProfileColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 32),
          // Stats row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildImpactStatItem(
                label: 'Total Reported',
                value: totalIssues.toString(),
                icon: Icons.report_problem_outlined,
              ),
              Container(width: 1, height: 50, color: ProfileColors.borderLight),
              _buildImpactStatItem(
                label: 'Resolved',
                value: resolvedIssues.toString(),
                icon: Icons.check_circle_outline,
                color: ProfileColors.successGreen,
              ),
              Container(width: 1, height: 50, color: ProfileColors.borderLight),
              _buildImpactStatItem(
                label: 'Pending',
                value: pendingIssues.toString(),
                icon: Icons.pending_outlined,
                color: ProfileColors.accentOrange,
              ),
            ],
          ),
          const SizedBox(height: 24),
          // Explanation text
          Text(
            'Your impact score is calculated based on how many of your reported issues have been resolved.',
            textAlign: TextAlign.center,
            style: GoogleFonts.roboto(
              fontSize: 12,
              color: ProfileColors.textSecondary,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildImpactStatItem({
    required String label,
    required String value,
    required IconData icon,
    Color? color,
  }) {
    return Column(
      children: [
        Icon(icon, size: 24, color: color ?? ProfileColors.textSecondary),
        const SizedBox(height: 8),
        Text(
          value,
          style: GoogleFonts.poppins(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: ProfileColors.textPrimary,
          ),
        ),
        Text(
          label,
          style: GoogleFonts.roboto(
            fontSize: 10,
            color: ProfileColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildReportsList() {
    final filteredReports = _getFilteredReports();

    if (filteredReports.isEmpty) {
      return Container(
        margin: const EdgeInsets.all(20),
        padding: const EdgeInsets.all(40),
        child: Column(
          children: [
            Icon(
              Icons.inbox_outlined,
              size: 48,
              color: ProfileColors.textSecondary,
            ),
            const SizedBox(height: 12),
            Text(
              _selectedTab == ReportFilterTab.RESOLVED
                  ? 'No resolved issues yet'
                  : 'No reports found',
              style: GoogleFonts.roboto(
                fontSize: 14,
                color: ProfileColors.textSecondary,
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      itemCount: filteredReports.length,
      itemBuilder: (context, index) {
        return _buildReportCard(filteredReports[index]);
      },
    );
  }

  Widget _buildReportCard(CivicReport report) {
    final isResolved = report.status == 'RESOLVED';

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
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
          Stack(
            children: [
              ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(16),
                ),
                child: CachedNetworkImage(
                  imageUrl: ApiService.imageUrl(report.imageUrl),
                  height: 160,
                  width: double.infinity,
                  fit: BoxFit.cover,
                  placeholder: (_, __) => Container(
                    height: 160,
                    color: ProfileColors.borderLight,
                    child: const Center(
                      child: CircularProgressIndicator(
                        color: ProfileColors.accentOrange,
                      ),
                    ),
                  ),
                  errorWidget: (_, __, ___) => Container(
                    height: 160,
                    color: ProfileColors.borderLight,
                    child: const Icon(Icons.image_not_supported, size: 40),
                  ),
                ),
              ),
              Positioned(
                top: 12,
                left: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: _getPriorityColor(
                      report.priority ?? 'MEDIUM_PRIORITY',
                    ),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    _formatPriority(report.priority ?? 'MEDIUM_PRIORITY'),
                    style: GoogleFonts.roboto(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
              if (isResolved)
                Positioned(
                  top: 12,
                  right: 12,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: ProfileColors.successGreen,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      'RESOLVED',
                      style: GoogleFonts.roboto(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
            ],
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  report.title,
                  style: GoogleFonts.poppins(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: ProfileColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(
                      Icons.location_on,
                      size: 14,
                      color: ProfileColors.textSecondary,
                    ),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        report.location,
                        style: GoogleFonts.roboto(
                          fontSize: 12,
                          color: ProfileColors.textSecondary,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  'REF ID: ${report.referenceId ?? report.id}',
                  style: GoogleFonts.roboto(
                    fontSize: 12,
                    color: ProfileColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 16),
                _buildStatusTimeline(report),
                const SizedBox(height: 16),
                // Supporters badge only (removed Monitor button)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: ProfileColors.textPrimary,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '+${report.supportCount}',
                        style: GoogleFonts.roboto(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        'SUPPORTERS',
                        style: GoogleFonts.roboto(
                          fontSize: 10,
                          color: Colors.white70,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusTimeline(CivicReport report) {
    final isResolved = report.status == 'RESOLVED';
    final isInProgress =
        report.status == 'IN_PROGRESS' || report.statusUpdate != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildTimelineItem(
          completed: true,
          label: 'Report Submitted',
          date: _formatDate(report.timestamp),
        ),
        if (isInProgress || isResolved) ...[
          _buildTimelineConnector(completed: true),
          _buildTimelineItem(
            completed: true,
            label: 'In Progress',
            date: report.statusUpdate ?? 'Processing',
            isWarning: !isResolved,
          ),
          if (!isResolved && report.statusUpdateMessage != null)
            Container(
              margin: const EdgeInsets.only(left: 24, top: 8),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: ProfileColors.statusYellow,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                '"${report.statusUpdateMessage}"',
                style: GoogleFonts.roboto(
                  fontSize: 12,
                  fontStyle: FontStyle.italic,
                  color: ProfileColors.textPrimary,
                ),
              ),
            ),
        ],
        _buildTimelineConnector(completed: isResolved),
        _buildTimelineItem(
          completed: isResolved,
          label: 'Resolution Confirmed',
          date: isResolved ? 'Completed' : 'Estimated: 2-3 days',
        ),
      ],
    );
  }

  Widget _buildTimelineItem({
    required bool completed,
    required String label,
    required String date,
    bool isWarning = false,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: completed ? ProfileColors.accentOrange : Colors.white,
            border: Border.all(
              color: completed
                  ? ProfileColors.accentOrange
                  : ProfileColors.textSecondary,
              width: 2,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    label,
                    style: GoogleFonts.roboto(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: completed
                          ? ProfileColors.textPrimary
                          : ProfileColors.textSecondary,
                    ),
                  ),
                  if (isWarning) ...[
                    const SizedBox(width: 6),
                    Icon(
                      Icons.circle,
                      size: 8,
                      color: ProfileColors.accentOrange,
                    ),
                  ],
                ],
              ),
              Text(
                date,
                style: GoogleFonts.roboto(
                  fontSize: 11,
                  color: ProfileColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTimelineConnector({required bool completed}) {
    return Container(
      margin: const EdgeInsets.only(left: 7),
      width: 2,
      height: 24,
      color: completed ? ProfileColors.accentOrange : ProfileColors.borderLight,
    );
  }

  Color _getPriorityColor(String priority) {
    switch (priority) {
      case 'HIGH_PRIORITY':
        return ProfileColors.priorityHigh;
      case 'MEDIUM_PRIORITY':
        return ProfileColors.textTan;
      default:
        return ProfileColors.textSecondary;
    }
  }

  String _formatPriority(String priority) {
    switch (priority) {
      case 'HIGH_PRIORITY':
        return 'HIGH PRIORITY';
      case 'MEDIUM_PRIORITY':
        return 'MEDIUM PRIORITY';
      default:
        return 'LOW PRIORITY';
    }
  }

  String _formatDate(DateTime date) {
    final months = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    return '${months[date.month - 1]} ${date.day}, ${date.year}';
  }

  Widget _buildFAB() {
    return FloatingActionButton.extended(
      onPressed: () async {
        await Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const ReportIssueScreen()),
        );
        // Refresh data when returning
        _refreshProfileData();
      },
      backgroundColor: ProfileColors.accentOrange,
      icon: const Icon(Icons.add, color: Colors.white),
      label: Text(
        'NEW REPORT',
        style: GoogleFonts.roboto(
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
      ),
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
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(0, Icons.home, 'Home'),
              _buildNavItem(1, Icons.explore, 'Explore'),
              _buildNavItem(2, Icons.person, 'Profile'),
              _buildNavItem(3, Icons.warning_amber_rounded, 'Issues'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(int index, IconData icon, String label) {
    bool isActive = _currentNavIndex == index;
    return InkWell(
      onTap: () {
        if (index == 0) {
          // Navigate to Home
          Navigator.pushReplacementNamed(context, '/home');
        } else if (index == 1) {
          // Navigate to Explore
          Navigator.pushReplacementNamed(context, '/explore');
        } else if (index == 3) {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const ReportIssueScreen()),
          ).then((_) => _refreshProfileData());
        } else {
          setState(() => _currentNavIndex = index);
        }
      },
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 24,
              color: isActive
                  ? ProfileColors.accentOrange
                  : ProfileColors.textSecondary,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: GoogleFonts.roboto(
                fontSize: 11,
                color: isActive
                    ? ProfileColors.accentOrange
                    : ProfileColors.textSecondary,
                fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// lib/screens/verification_screen.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:geolocator/geolocator.dart';
import '../models/verification_model.dart';
import '../services/api_service.dart';
import '../theme/app_colors.dart';
import '../widgets/app_toast.dart';

class VerificationScreen extends StatefulWidget {
  const VerificationScreen({super.key});

  @override
  State<VerificationScreen> createState() => _VerificationScreenState();
}

class _VerificationScreenState extends State<VerificationScreen> {
  List<VerificationRequestModel> _requests = [];
  bool _isLoading = true;
  bool _isVoting = false;
  double? _userLat;
  double? _userLng;
  int _currentPage = 0;
  final PageController _pageController = PageController();

  @override
  void initState() {
    super.initState();
    _fetchLocationAndLoad();
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  // ─── Location ────────────────────────────────────────────────────────────

  Future<void> _fetchLocationAndLoad() async {
    setState(() => _isLoading = true);
    await _fetchLocation();
    await _loadVerifications();
    if (mounted) setState(() => _isLoading = false);
  }

  Future<void> _fetchLocation() async {
    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        return;
      }
      final serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) return;

      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.medium,
        timeLimit: const Duration(seconds: 15),
      );
      _userLat = position.latitude;
      _userLng = position.longitude;
    } catch (e) {
      debugPrint('Verification — location error: $e');
    }
  }

  // ─── Data ────────────────────────────────────────────────────────────────

  Future<void> _loadVerifications() async {
    // Lahore city centre fallback if GPS is unavailable
    final lat = _userLat ?? 31.5204;
    final lng = _userLng ?? 74.3587;

    final result = await ApiService.getPendingVerifications(lat, lng);
    if (!mounted) return;

    if (result['success'] == true) {
      final raw = result['data']['requests'] as List<dynamic>;
      setState(() {
        _requests = raw
            .map((r) => VerificationRequestModel.fromJson(r as Map<String, dynamic>))
            .toList();
      });
    }
  }

  // ─── Voting ──────────────────────────────────────────────────────────────

  Future<void> _submitVote(VerificationRequestModel request, String vote) async {
    if (_isVoting) return;
    setState(() => _isVoting = true);

    try {
      final result = await ApiService.submitVerificationVote(
        request.requestId,
        vote,
        _userLat,
        _userLng,
      );

      if (!mounted) return;

      if (result['success'] == true) {
        final msg = vote == 'YES'
            ? 'Marked as a real issue. Thank you!'
            : 'Marked as false report. Thank you!';
        showAppToast(context, message: msg, isError: false);

        setState(() {
          final idx = _requests.indexOf(request);
          _requests.remove(request);

          if (_requests.isNotEmpty) {
            // Stay at the same index (next item slides in), unless we were last
            final targetPage =
                idx < _requests.length ? idx : _requests.length - 1;
            _currentPage = targetPage;
            _pageController.jumpToPage(targetPage);
          } else {
            _currentPage = 0;
          }
        });
      } else {
        showAppToast(
          context,
          message: result['error'] as String? ?? 'Vote failed. Please try again.',
          isError: true,
        );
      }
    } catch (_) {
      if (mounted) {
        showAppToast(context, message: 'Cannot connect to server.', isError: true);
      }
    } finally {
      if (mounted) setState(() => _isVoting = false);
    }
  }

  // ─── Helpers ─────────────────────────────────────────────────────────────

  String _timeAgo(String isoString) {
    try {
      final dt = DateTime.parse(isoString).toLocal();
      final diff = DateTime.now().difference(dt);
      if (diff.inMinutes < 1) return 'JUST NOW';
      if (diff.inMinutes < 60) return '${diff.inMinutes} MINUTES AGO';
      if (diff.inHours < 24) return '${diff.inHours} HOURS AGO';
      return '${diff.inDays} DAYS AGO';
    } catch (_) {
      return 'RECENTLY';
    }
  }

  String _distanceLabel(double metres) {
    if (metres >= 1000) {
      return '${(metres / 1000).toStringAsFixed(1)} KM FROM YOU';
    }
    return '${metres.toInt()} M FROM YOU';
  }

  String _yesLabel(String category) {
    switch (category.toUpperCase()) {
      case 'POTHOLE':
        return 'YES, POTHOLE EXISTS';
      case 'TRASH':
        return 'YES, TRASH EXISTS';
      default:
        return 'YES, ISSUE EXISTS';
    }
  }

  // ─── Build ───────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Stack(
          children: [
            Column(
              children: [
                _buildTopBar(),
                Expanded(child: _buildBody()),
                _buildFooter(),
              ],
            ),
            // Voting overlay — covers entire screen to block interaction
            if (_isVoting)
              Container(
                color: Colors.black54,
                child: const Center(
                  child: CircularProgressIndicator(color: AppColors.goldPrimary),
                ),
              ),
          ],
        ),
      ),
    );
  }

  // ── Top bar ──────────────────────────────────────────────────────────────

  Widget _buildTopBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
      child: Row(
        children: [
          // Back arrow
          GestureDetector(
            onTap: () => Navigator.of(context).pop(),
            child: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: const Color(0xFF1A1A1A),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.arrow_back_ios_new,
                color: AppColors.textPrimary,
                size: 18,
              ),
            ),
          ),

          // Title centred
          Expanded(
            child: Column(
              children: [
                Text(
                  'VERIFICATION',
                  style: GoogleFonts.rajdhani(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                    letterSpacing: 3.0,
                  ),
                ),
                Container(
                  height: 2,
                  width: 80,
                  decoration: BoxDecoration(
                    color: AppColors.goldPrimary,
                    borderRadius: BorderRadius.circular(1),
                  ),
                ),
              ],
            ),
          ),

          // Info icon
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: const Color(0xFF1A1A1A),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: AppColors.goldPrimary.withOpacity(0.4),
                width: 1,
              ),
            ),
            child: const Icon(
              Icons.info_outline_rounded,
              color: AppColors.goldPrimary,
              size: 20,
            ),
          ),
        ],
      ),
    );
  }

  // ── Body ─────────────────────────────────────────────────────────────────

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: AppColors.goldPrimary),
      );
    }

    if (_requests.isEmpty) {
      return _buildEmptyState();
    }

    return Column(
      children: [
        // Page counter
        Padding(
          padding: const EdgeInsets.only(bottom: 6),
          child: Text(
            '${_currentPage + 1} / ${_requests.length}',
            style: GoogleFonts.roboto(
              fontSize: 12,
              color: Colors.grey.shade500,
              letterSpacing: 2.0,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Expanded(
          child: PageView.builder(
            controller: _pageController,
            itemCount: _requests.length,
            onPageChanged: (i) => setState(() => _currentPage = i),
            itemBuilder: (context, index) => _buildCard(_requests[index]),
          ),
        ),
      ],
    );
  }

  // ── Empty state ──────────────────────────────────────────────────────────

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.check_circle_outline_rounded,
              size: 72,
              color: AppColors.goldPrimary.withOpacity(0.55),
            ),
            const SizedBox(height: 24),
            Text(
              "You're all caught up!",
              textAlign: TextAlign.center,
              style: GoogleFonts.rajdhani(
                fontSize: 26,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'No nearby issues to verify.\nCheck back later.',
              textAlign: TextAlign.center,
              style: GoogleFonts.roboto(
                fontSize: 14,
                color: Colors.grey.shade500,
                height: 1.7,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Verification card ────────────────────────────────────────────────────

  Widget _buildCard(VerificationRequestModel request) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Title
          Text(
            request.title,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: GoogleFonts.rajdhani(
              fontSize: 26,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
              height: 1.1,
              letterSpacing: 0.5,
            ),
          ),
          const SizedBox(height: 8),

          // ── Meta row
          Row(
            children: [
              Text(
                '📍 ${_distanceLabel(request.distanceM)}',
                style: GoogleFonts.roboto(
                  fontSize: 12,
                  color: AppColors.goldPrimary,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.6,
                ),
              ),
              const SizedBox(width: 16),
              Text(
                '🕐 ${_timeAgo(request.createdAt)}',
                style: GoogleFonts.roboto(
                  fontSize: 12,
                  color: AppColors.goldPrimary,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.6,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // ── Image with overlaid badges
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Stack(
                fit: StackFit.expand,
                children: [
                  // Report image
                  CachedNetworkImage(
                    imageUrl: ApiService.imageUrl(request.imageUrl),
                    fit: BoxFit.cover,
                    placeholder: (_, __) => Container(
                      color: const Color(0xFF1A1A1A),
                      child: const Center(
                        child: CircularProgressIndicator(
                          color: AppColors.goldPrimary,
                          strokeWidth: 2,
                        ),
                      ),
                    ),
                    errorWidget: (_, __, ___) => Container(
                      color: const Color(0xFF1A1A1A),
                      child: const Center(
                        child: Icon(
                          Icons.broken_image_outlined,
                          color: Colors.grey,
                          size: 48,
                        ),
                      ),
                    ),
                  ),

                  // Bottom gradient for badge legibility
                  Positioned(
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: 110,
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.bottomCenter,
                          end: Alignment.topCenter,
                          colors: [
                            Colors.black.withOpacity(0.75),
                            Colors.transparent,
                          ],
                        ),
                      ),
                    ),
                  ),

                  // Target zone badge — bottom left
                  Positioned(
                    bottom: 12,
                    left: 12,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.78),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: AppColors.goldPrimary.withOpacity(0.55),
                          width: 1,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(
                              color: AppColors.goldPrimary,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            'TARGET: ${request.category}',
                            style: GoogleFonts.roboto(
                              fontSize: 11,
                              color: AppColors.textPrimary,
                              fontWeight: FontWeight.w600,
                              letterSpacing: 1.2,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Vote progress badge — bottom right
                  Positioned(
                    bottom: 12,
                    right: 12,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.78),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        '${request.totalVotes}/${request.minVotes} VOTES',
                        style: GoogleFonts.roboto(
                          fontSize: 11,
                          color: Colors.grey.shade300,
                          fontWeight: FontWeight.w500,
                          letterSpacing: 1.0,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // ── YES button
          _VoteButton(
            label: _yesLabel(request.category),
            icon: Icons.visibility_rounded,
            isPrimary: true,
            enabled: !_isVoting,
            onTap: () => _submitVote(request, 'YES'),
          ),

          const SizedBox(height: 10),

          // ── NO button
          _VoteButton(
            label: 'NO, FALSE REPORT',
            icon: Icons.highlight_off_rounded,
            isPrimary: false,
            enabled: !_isVoting,
            onTap: () => _submitVote(request, 'NO'),
          ),

          const SizedBox(height: 12),
        ],
      ),
    );
  }

  // ── Footer ───────────────────────────────────────────────────────────────

  Widget _buildFooter() {
    return Padding(
      padding: const EdgeInsets.only(top: 6, bottom: 14, left: 24, right: 24),
      child: Text(
        'REPORTS HELP KEEP OUR NEIGHBORHOODS SAFE AND BRIGHT',
        textAlign: TextAlign.center,
        style: GoogleFonts.roboto(
          fontSize: 10,
          color: Colors.grey.shade600,
          letterSpacing: 1.4,
          fontWeight: FontWeight.w400,
        ),
      ),
    );
  }
}

// ─── Vote button widget ───────────────────────────────────────────────────

class _VoteButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isPrimary;
  final bool enabled;
  final VoidCallback onTap;

  const _VoteButton({
    required this.label,
    required this.icon,
    required this.isPrimary,
    required this.enabled,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final fg = isPrimary ? AppColors.background : AppColors.textPrimary;

    return SizedBox(
      width: double.infinity,
      height: 52,
      child: GestureDetector(
        onTap: enabled ? onTap : null,
        child: AnimatedOpacity(
          opacity: enabled ? 1.0 : 0.5,
          duration: const Duration(milliseconds: 200),
          child: Container(
            decoration: BoxDecoration(
              color: isPrimary ? AppColors.goldPrimary : const Color(0xFF111111),
              borderRadius: BorderRadius.circular(12),
              border: isPrimary
                  ? null
                  : Border.all(color: Colors.grey.shade700, width: 1),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, size: 20, color: fg),
                const SizedBox(width: 10),
                Text(
                  label,
                  style: GoogleFonts.rajdhani(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: fg,
                    letterSpacing: 1.5,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

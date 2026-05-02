import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../theme/app_colors.dart';
import '../widgets/app_toast.dart';

/// Citizen compares before/after photos and confirms or rejects the fix (AWAITING_FEEDBACK).
class ResolutionConfirmScreen extends StatefulWidget {
  const ResolutionConfirmScreen({super.key, required this.reportId});

  final int reportId;

  @override
  State<ResolutionConfirmScreen> createState() =>
      _ResolutionConfirmScreenState();
}

class _ResolutionConfirmScreenState extends State<ResolutionConfirmScreen> {
  bool _busy = false;
  bool _loading = true;
  String? _error;
  String _displayId = '';
  String _title = '';
  String _beforeUrl = '';
  String _afterUrl = '';
  bool _canConfirm = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    if (widget.reportId <= 0) {
      setState(() {
        _loading = false;
        _error = 'Invalid report.';
      });
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    final res = await ApiService.getResolutionDetail(widget.reportId);
    if (!mounted) return;
    if (res['success'] == true) {
      final d = res['data'] as Map<String, dynamic>;
      setState(() {
        _displayId = (d['display_id'] ?? '').toString();
        _title = (d['title'] ?? '').toString();
        _beforeUrl = (d['image_url'] ?? '').toString().trim();
        _afterUrl = (d['after_image_url'] ?? '').toString().trim();
        _canConfirm = d['can_confirm'] == true;
        _loading = false;
      });
    } else {
      setState(() {
        _error = res['error']?.toString() ?? 'Could not load report.';
        _loading = false;
      });
    }
  }

  Future<void> _submit(bool confirmed) async {
    if (widget.reportId <= 0) {
      showAppToast(context, message: 'Invalid report.');
      return;
    }
    if (confirmed && !_canConfirm) {
      showAppToast(
        context,
        message:
            'This report is not ready to confirm yet (wait for team proof, or refresh).',
      );
      return;
    }
    setState(() => _busy = true);
    final res = await ApiService.confirmReportResolution(
      reportId: widget.reportId,
      confirmed: confirmed,
    );
    if (!mounted) return;
    setState(() => _busy = false);

    if (res['success'] == true) {
      showAppToast(
        context,
        message: confirmed
            ? 'Thank you! Your report will be marked closed.'
            : 'Thanks — we asked the team to follow up.',
        isError: false,
      );
      Navigator.pop(context, true);
    } else {
      showAppToast(
        context,
        message: res['error']?.toString() ?? 'Could not update resolution.',
      );
    }
  }

  Widget _photoColumn(String label, String url, {required bool isAfter}) {
    final full = ApiService.imageUrl(url);
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            label,
            textAlign: TextAlign.center,
            style: GoogleFonts.poppins(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppColors.goldSecondary,
            ),
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: AspectRatio(
              aspectRatio: 3 / 4,
              child: url.isEmpty
                  ? Container(
                      color: Colors.black26,
                      alignment: Alignment.center,
                      padding: const EdgeInsets.all(12),
                      child: Text(
                        isAfter
                            ? 'No after photo yet'
                            : 'No before photo',
                        textAlign: TextAlign.center,
                        style: GoogleFonts.roboto(
                          color: Colors.white54,
                          fontSize: 12,
                        ),
                      ),
                    )
                  : CachedNetworkImage(
                      imageUrl: full,
                      fit: BoxFit.cover,
                      placeholder: (_, __) => const Center(
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                      errorWidget: (_, __, ___) => Container(
                        color: Colors.black26,
                        child: const Icon(Icons.broken_image,
                            color: Colors.white54),
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (widget.reportId <= 0) {
      return Scaffold(
        backgroundColor: AppColors.darkBrown,
        appBar: AppBar(
          backgroundColor: AppColors.darkBrown,
          foregroundColor: AppColors.textPrimary,
          title: const Text('Resolution'),
        ),
        body: Center(
          child: Text(
            'Missing report reference.',
            style: GoogleFonts.roboto(color: AppColors.textPrimary),
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.darkBrown,
      appBar: AppBar(
        backgroundColor: AppColors.darkBrown,
        foregroundColor: AppColors.textPrimary,
        elevation: 0,
        title: Text(
          'Verify the fix',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w600),
        ),
        actions: [
          if (!_loading)
            IconButton(
              onPressed: _busy ? null : _load,
              icon: const Icon(Icons.refresh),
            ),
        ],
      ),
      body: SafeArea(
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            _error!,
                            textAlign: TextAlign.center,
                            style: GoogleFonts.roboto(color: Colors.white70),
                          ),
                          const SizedBox(height: 16),
                          TextButton(
                            onPressed: _load,
                            child: const Text('Retry'),
                          ),
                        ],
                      ),
                    ),
                  )
                : SingleChildScrollView(
                    padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          _displayId.isNotEmpty
                              ? _displayId
                              : '#SR-${widget.reportId.toString().padLeft(4, '0')}',
                          style: GoogleFonts.poppins(
                            fontSize: 20,
                            fontWeight: FontWeight.w700,
                            color: AppColors.goldPrimary,
                          ),
                        ),
                        if (_title.isNotEmpty) ...[
                          const SizedBox(height: 6),
                          Text(
                            _title,
                            style: GoogleFonts.roboto(
                              fontSize: 14,
                              color: AppColors.goldText,
                              height: 1.35,
                            ),
                          ),
                        ],
                        const SizedBox(height: 20),
                        Text(
                          'Compare the original issue with the municipal after photo. '
                          'Does it look resolved?',
                          style: GoogleFonts.roboto(
                            fontSize: 14,
                            height: 1.5,
                            color: AppColors.goldText,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _photoColumn('Before (your report)', _beforeUrl,
                                isAfter: false),
                            const SizedBox(width: 12),
                            _photoColumn('After (repair)', _afterUrl,
                                isAfter: true),
                          ],
                        ),
                        if (!_canConfirm) ...[
                          const SizedBox(height: 16),
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.amber.withValues(alpha: 0.15),
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(
                                color: Colors.amber.withValues(alpha: 0.4),
                              ),
                            ),
                            child: Text(
                              'You can confirm once the team has uploaded an after photo '
                              'and the report is awaiting your feedback. Pull to refresh '
                              'or use the reload icon.',
                              style: GoogleFonts.roboto(
                                fontSize: 12,
                                color: Colors.amber.shade100,
                                height: 1.4,
                              ),
                            ),
                          ),
                        ],
                        const SizedBox(height: 28),
                        ElevatedButton(
                          onPressed:
                              _busy || !_canConfirm ? null : () => _submit(true),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.goldPrimary,
                            foregroundColor: AppColors.darkBrown,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: Text(
                            'Yes — issue is fixed',
                            style: GoogleFonts.poppins(
                                fontWeight: FontWeight.w600),
                          ),
                        ),
                        const SizedBox(height: 12),
                        OutlinedButton(
                          onPressed: _busy ? null : () => _submit(false),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: AppColors.textPrimary,
                            side: const BorderSide(
                                color: AppColors.goldSecondary),
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: Text(
                            'No — still a problem',
                            style: GoogleFonts.poppins(
                                fontWeight: FontWeight.w600),
                          ),
                        ),
                        if (_busy)
                          const Padding(
                            padding: EdgeInsets.only(top: 24),
                            child: Center(child: CircularProgressIndicator()),
                          ),
                      ],
                    ),
                  ),
      ),
    );
  }
}

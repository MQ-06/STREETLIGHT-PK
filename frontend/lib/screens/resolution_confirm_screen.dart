import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../theme/app_colors.dart';
import '../widgets/app_toast.dart';

/// Citizen confirms or rejects municipal "issue fixed" after push (AWAITING_FEEDBACK).
class ResolutionConfirmScreen extends StatefulWidget {
  const ResolutionConfirmScreen({super.key, required this.reportId});

  final int reportId;

  @override
  State<ResolutionConfirmScreen> createState() =>
      _ResolutionConfirmScreenState();
}

class _ResolutionConfirmScreenState extends State<ResolutionConfirmScreen> {
  bool _busy = false;

  Future<void> _submit(bool confirmed) async {
    if (widget.reportId <= 0) {
      showAppToast(context, message: 'Invalid report.');
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
            ? 'Thanks — your report is being closed.'
            : 'Thanks — we notified the team to follow up.',
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
          'Confirm fix',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w600),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Report #SR-${widget.reportId.toString().padLeft(4, '0')}',
                style: GoogleFonts.poppins(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  color: AppColors.goldPrimary,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'The municipal team marked this issue as fixed and shared an after photo. '
                'Does it look resolved from your perspective?',
                style: GoogleFonts.roboto(
                  fontSize: 15,
                  height: 1.5,
                  color: AppColors.goldText,
                ),
              ),
              const Spacer(),
              ElevatedButton(
                onPressed: _busy ? null : () => _submit(true),
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
                  style: GoogleFonts.poppins(fontWeight: FontWeight.w600),
                ),
              ),
              const SizedBox(height: 12),
              OutlinedButton(
                onPressed: _busy ? null : () => _submit(false),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.textPrimary,
                  side: const BorderSide(color: AppColors.goldSecondary),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  'No — still a problem',
                  style: GoogleFonts.poppins(fontWeight: FontWeight.w600),
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

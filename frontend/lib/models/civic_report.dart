/// Data model for civic issue reports
class CivicReport {
  final String id;
  final String reporterId;
  final String reporterName;
  final String reporterInitials;
  final String reporterAvatar; // hex color string
  final DateTime timestamp;
  final String location;
  final String issueCategory; // "POTHOLE" or "TRASH" only
  final String title;
  final String description;
  final String imageUrl;
  final int views;
  final int verificationCount;
  final int supportCount;
  final List<String> verifications;
  
  // New fields for profile screen
  final String? priority; // "HIGH_PRIORITY", "MEDIUM_PRIORITY", "LOW_PRIORITY"
  final String? referenceId; // e.g., "#SR-9921"
  final String? statusUpdate; // e.g., "Technician Assigned - Oct 25"
  final String? statusUpdateMessage; // e.g., "Team Alpha dispatched..."
  final String? statusOverride; // Override computed status: "REPORTED", "IN_PROGRESS", "RESOLVED"

  CivicReport({
    required this.id,
    required this.reporterId,
    required this.reporterName,
    required this.reporterInitials,
    required this.reporterAvatar,
    required this.timestamp,
    required this.location,
    required this.issueCategory,
    required this.title,
    required this.description,
    required this.imageUrl,
    required this.views,
    required this.verificationCount,
    required this.supportCount,
    required this.verifications,
    this.priority,
    this.referenceId,
    this.statusUpdate,
    this.statusUpdateMessage,
    this.statusOverride,
  });

  /// Computed status based on verification count thresholds or override
  String get status {
    if (statusOverride != null) return statusOverride!;
    if (verificationCount >= 5) return 'VERIFIED';
    if (verificationCount >= 2) return 'IN_PROGRESS';
    return 'REPORTED';
  }

  /// Get time ago string from timestamp
  String get timeAgo {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }
  
  /// Check if this is the user's own report
  bool isUserReport(String userId) => reporterId == userId;
}

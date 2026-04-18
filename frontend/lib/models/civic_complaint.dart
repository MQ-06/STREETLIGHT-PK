/// Data model for civic complaints displayed on the explore map
class CivicComplaint {
  final String id;
  final String referenceId;
  final String title;
  final String description;
  final String category; // "POTHOLE" or "GARBAGE"
  final String priority; // "CRITICAL", "PENDING", "RESOLVED"
  final String location;
  final String address;
  final double latitude;
  final double longitude;
  final DateTime reportedDate;
  final String status; // "CRITICAL", "PENDING", "RESOLVED"
  final String timeAgo;
  final String region;
  final bool isPriority;
  final String imageUrl;
  final int supportCount;
  final int verifyCount;
  final double? combinedScore;
  final double? aiConfidence;
  final String? verificationStatus;
  final String reporterName;
  final String reporterInitials;

  CivicComplaint({
    required this.id,
    required this.referenceId,
    required this.title,
    required this.description,
    required this.category,
    required this.priority,
    required this.location,
    required this.address,
    required this.latitude,
    required this.longitude,
    required this.reportedDate,
    required this.status,
    required this.timeAgo,
    required this.region,
    required this.isPriority,
    this.imageUrl = '',
    this.supportCount = 0,
    this.verifyCount = 0,
    this.combinedScore,
    this.aiConfidence,
    this.verificationStatus,
    this.reporterName = '',
    this.reporterInitials = '',
  });
}

/// Regional statistics for the explore screen
class RegionalStats {
  final String region;
  final int criticalCount;
  final int pendingCount;
  final int resolvedCount;
  final List<String> categories;

  RegionalStats({
    required this.region,
    required this.criticalCount,
    required this.pendingCount,
    required this.resolvedCount,
    required this.categories,
  });
}

/// Map marker data
class MapMarkerData {
  final String id;
  final double latitude;
  final double longitude;
  final String category;
  final String priority;
  final String title;

  MapMarkerData({
    required this.id,
    required this.latitude,
    required this.longitude,
    required this.category,
    required this.priority,
    required this.title,
  });
}

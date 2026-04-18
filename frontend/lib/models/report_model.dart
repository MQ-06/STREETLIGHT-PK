// lib/models/report_model.dart

class ReportModel {
  final int id;
  final int reporterId;
  final String reporterName;
  final String reporterInitials;
  final String? reporterAvatarUrl;
  final DateTime timestamp;
  final String location;
  final String locationCity;
  final double? locationLat;
  final double? locationLng;
  final String issueCategory;
  final String title;
  final String description;
  final String imageUrl;
  final int views;
  final int supportCount;
  final int verifyCount;
  final int commentCount;
  final String status;
  final double? combinedScore;
  final double? aiConfidence;
  final String? verificationStatus;
  bool hasSupported;
  bool hasVerified;

  ReportModel({
    required this.id,
    required this.reporterId,
    required this.reporterName,
    required this.reporterInitials,
    this.reporterAvatarUrl,
    required this.timestamp,
    required this.location,
    required this.locationCity,
    this.locationLat,
    this.locationLng,
    required this.issueCategory,
    required this.title,
    required this.description,
    required this.imageUrl,
    required this.views,
    required this.supportCount,
    required this.verifyCount,
    required this.commentCount,
    required this.status,
    this.combinedScore,
    this.aiConfidence,
    this.verificationStatus,
    required this.hasSupported,
    required this.hasVerified,
  });

  factory ReportModel.fromJson(Map<String, dynamic> json) {
    return ReportModel(
      id: json['id'] as int,
      reporterId: json['reporter_id'] as int,
      reporterName: json['reporter_name'] as String,
      reporterInitials: json['reporter_initials'] as String,
      reporterAvatarUrl: json['reporter_avatar_url'] as String?,
      timestamp: DateTime.parse(json['timestamp'] as String),
      location: json['location'] as String,
      locationCity: json['location_city'] as String? ?? '',
      locationLat: (json['location_lat'] as num?)?.toDouble(),
      locationLng: (json['location_lng'] as num?)?.toDouble(),
      issueCategory: json['issue_category'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      imageUrl: json['image_url'] as String? ?? '',
      views: json['views'] as int? ?? 0,
      supportCount: json['support_count'] as int? ?? 0,
      verifyCount: json['verify_count'] as int? ?? 0,
      commentCount: json['comment_count'] as int? ?? 0,
      status: json['status'] as String? ?? 'REPORTED',
      combinedScore: (json['combined_score'] as num?)?.toDouble(),
      aiConfidence: (json['ai_confidence'] as num?)?.toDouble(),
      verificationStatus: json['verification_status'] as String?,
      hasSupported: json['has_supported'] as bool? ?? false,
      hasVerified: json['has_verified'] as bool? ?? false,
    );
  }

  String get timeAgo {
    final diff = DateTime.now().difference(timestamp);
    if (diff.inMinutes < 1) return 'just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return '${(diff.inDays / 7).floor()}w ago';
  }
}

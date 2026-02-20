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
  final String issueCategory;
  final String title;
  final String description;
  final String imageUrl;
  final int views;
  final int supportCount;
  final int verifyCount;
  final String status;
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
    required this.issueCategory,
    required this.title,
    required this.description,
    required this.imageUrl,
    required this.views,
    required this.supportCount,
    required this.verifyCount,
    required this.status,
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
      issueCategory: json['issue_category'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      imageUrl: json['image_url'] as String? ?? '',
      views: json['views'] as int? ?? 0,
      supportCount: json['support_count'] as int? ?? 0,
      verifyCount: json['verify_count'] as int? ?? 0,
      status: json['status'] as String? ?? 'REPORTED',
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
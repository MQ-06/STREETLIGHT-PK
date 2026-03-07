// lib/models/verification_model.dart

class VerificationRequestModel {
  final int requestId;
  final int reportId;
  final String title;
  final String imageUrl;
  final String category;
  final double distanceM;
  final String createdAt;
  final int totalVotes;
  final int minVotes;

  VerificationRequestModel({
    required this.requestId,
    required this.reportId,
    required this.title,
    required this.imageUrl,
    required this.category,
    required this.distanceM,
    required this.createdAt,
    required this.totalVotes,
    required this.minVotes,
  });

  factory VerificationRequestModel.fromJson(Map<String, dynamic> json) {
    return VerificationRequestModel(
      requestId:  json['request_id'] as int,
      reportId:   json['report_id'] as int,
      title:      json['title'] as String,
      imageUrl:   json['image_url'] as String? ?? '',
      category:   json['category'] as String,
      distanceM:  (json['distance_m'] as num).toDouble(),
      createdAt:  json['created_at'] as String,
      totalVotes: json['total_votes'] as int? ?? 0,
      minVotes:   json['min_votes'] as int? ?? 3,
    );
  }
}

class VerificationStatusModel {
  final int requestId;
  final String status;
  final int totalVotes;
  final int yesVotes;
  final int noVotes;
  final int minVotes;
  final double? communityScore;
  final String createdAt;
  final String? completedAt;

  VerificationStatusModel({
    required this.requestId,
    required this.status,
    required this.totalVotes,
    required this.yesVotes,
    required this.noVotes,
    required this.minVotes,
    this.communityScore,
    required this.createdAt,
    this.completedAt,
  });

  factory VerificationStatusModel.fromJson(Map<String, dynamic> json) {
    return VerificationStatusModel(
      requestId:      json['request_id'] as int,
      status:         json['status'] as String,
      totalVotes:     json['total_votes'] as int? ?? 0,
      yesVotes:       json['yes_votes'] as int? ?? 0,
      noVotes:        json['no_votes'] as int? ?? 0,
      minVotes:       json['min_votes'] as int? ?? 3,
      communityScore: (json['community_score'] as num?)?.toDouble(),
      createdAt:      json['created_at'] as String,
      completedAt:    json['completed_at'] as String?,
    );
  }
}

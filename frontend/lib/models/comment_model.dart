// lib/models/comment_model.dart

class CommentModel {
  final int id;
  final int reportId;
  final int userId;
  final String text;
  final String userName;
  final String userInitials;
  final String? userAvatarUrl;
  final DateTime timestamp;
  final bool isOwnComment;

  const CommentModel({
    required this.id,
    required this.reportId,
    required this.userId,
    required this.text,
    required this.userName,
    required this.userInitials,
    this.userAvatarUrl,
    required this.timestamp,
    required this.isOwnComment,
  });

  factory CommentModel.fromJson(Map<String, dynamic> json) {
    return CommentModel(
      id: json['id'] as int,
      reportId: json['report_id'] as int,
      userId: json['user_id'] as int,
      text: json['text'] as String,
      userName: json['user_name'] as String,
      userInitials: json['user_initials'] as String,
      userAvatarUrl: json['user_avatar_url'] as String?,
      timestamp: DateTime.parse(json['created_at'] as String),
      isOwnComment: json['is_own_comment'] as bool? ?? false,
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

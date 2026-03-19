class AppNotification {
  final int id;
  final String type;
  final String title;
  final String? body;
  final String? entityType;
  final int? entityId;
  final Map<String, dynamic>? data;
  final DateTime createdAt;
  final DateTime? readAt;

  bool get isRead => readAt != null;

  const AppNotification({
    required this.id,
    required this.type,
    required this.title,
    required this.createdAt,
    this.body,
    this.entityType,
    this.entityId,
    this.data,
    this.readAt,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] as int,
      type: (json['type'] ?? '').toString(),
      title: (json['title'] ?? '').toString(),
      body: json['body']?.toString(),
      entityType: json['entity_type']?.toString(),
      entityId: json['entity_id'] is int ? (json['entity_id'] as int) : int.tryParse('${json['entity_id']}'),
      data: json['data'] is Map ? Map<String, dynamic>.from(json['data'] as Map) : null,
      createdAt: DateTime.tryParse((json['created_at'] ?? '').toString()) ?? DateTime.now(),
      readAt: json['read_at'] == null ? null : DateTime.tryParse(json['read_at'].toString()),
    );
  }
}


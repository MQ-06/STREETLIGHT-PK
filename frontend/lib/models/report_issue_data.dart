import 'dart:io';

/// Location data model for storing GPS and address information
class LocationData {
  final double latitude;
  final double longitude;
  final String address;
  final String city;
  final String state;
  final String zipCode;

  LocationData({
    required this.latitude,
    required this.longitude,
    required this.address,
    required this.city,
    required this.state,
    required this.zipCode,
  });

  Map<String, dynamic> toJson() {
    return {
      'latitude': latitude,
      'longitude': longitude,
      'address': address,
      'city': city,
      'state': state,
      'zipCode': zipCode,
    };
  }
}

/// Issue category enumeration
enum IssueCategory { POTHOLE, TRASH }

/// Complete report issue data model for form submission
class ReportIssueData {
  File? imageFile;
  String? imageLocalPath;
  LocationData? location;
  IssueCategory? issueCategory;
  String? description;
  DateTime? createdAt;
  String? tempId;

  ReportIssueData({
    this.imageFile,
    this.imageLocalPath,
    this.location,
    this.issueCategory,
    this.description,
    this.createdAt,
    this.tempId,
  });

  /// Convert to JSON for future backend integration
  Map<String, dynamic> toJson() {
    return {
      'imageLocalPath': imageLocalPath,
      'latitude': location?.latitude,
      'longitude': location?.longitude,
      'address': location?.address,
      'city': location?.city,
      'state': location?.state,
      'zipCode': location?.zipCode,
      'issueCategory': issueCategory?.name,
      'description': description,
      'createdAt': createdAt?.toIso8601String(),
      'tempId': tempId,
    };
  }

  /// Check if all required fields are filled
  bool isComplete() {
    return imageFile != null &&
        location != null &&
        issueCategory != null &&
        description != null &&
        description!.isNotEmpty;
  }
}

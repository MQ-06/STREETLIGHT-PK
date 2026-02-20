/// user_profile.dart data model
class UserProfile {
  String userId;
  String name;
  String profileImageUrl;
  String? profileImageLocalPath;
  String location;
  int impactScore;
  int totalReported;
  int totalFixed;
  int totalAided;
  DateTime joinedDate;

  UserProfile({
    required this.userId,
    required this.name,
    required this.profileImageUrl,
    this.profileImageLocalPath,
    required this.location,
    required this.impactScore,
    required this.totalReported,
    required this.totalFixed,
    required this.totalAided,
    required this.joinedDate,
  });

  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'name': name,
      'profileImageUrl': profileImageUrl,
      'profileImageLocalPath': profileImageLocalPath,
      'location': location,
      'impactScore': impactScore,
      'totalReported': totalReported,
      'totalFixed': totalFixed,
      'totalAided': totalAided,
      'joinedDate': joinedDate.toIso8601String(),
    };
  }
}

/// Impact metrics for user profile
class ImpactMetrics {
  final int totalReported;
  final int totalVerified;
  final int totalResolved;
  final double impactPercentage;
  final int impactScore;

  ImpactMetrics({
    required this.totalReported,
    required this.totalVerified,
    required this.totalResolved,
    required this.impactPercentage,
    required this.impactScore,
  });
}

/// Filter tabs for reports
enum ReportFilterTab {
  MY_REPORTS,
  RESOLVED,
  IMPACT,
}

/// Calculate impact metrics from user reports
ImpactMetrics calculateImpactMetrics(List<dynamic> userReports) {
  final total = userReports.length;
  int verified = 0;
  int resolved = 0;
  
  for (var report in userReports) {
    if (report.verificationCount >= 5) verified++;
    if (report.status == 'RESOLVED') resolved++;
  }
  
  final percentage = total == 0 ? 0.0 : (verified / total) * 100;
  final score = total == 0 ? 0 : ((verified / total) * 1000).toInt().clamp(0, 1000);
  
  return ImpactMetrics(
    totalReported: total,
    totalVerified: verified,
    totalResolved: resolved,
    impactPercentage: percentage,
    impactScore: score,
  );
}

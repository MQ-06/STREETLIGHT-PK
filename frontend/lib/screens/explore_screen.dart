import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/civic_complaint.dart';

/// Color palette for Explore screen
class ExploreColors {
  static const backgroundColor = Color(0xFFFFF8E7);
  static const cardBackground = Color(0xFFFFFFFF);
  static const primaryOrange = Color(0xFFC85A3A);
  static const textPrimary = Color(0xFF000000);
  static const textSecondary = Color(0xFF666666);
  static const criticalRed = Color(0xFFE53935);
  static const pendingGray = Color(0xFF888888);
  static const resolvedGreen = Color(0xFF4CAF50);
  static const potholeOrange = Color(0xFFC85A3A);
  static const garbageGray = Color(0xFF888888);
  static const borderLight = Color(0xFFEEEEEE);
}

class ExploreScreen extends StatefulWidget {
  const ExploreScreen({super.key});

  @override
  State<ExploreScreen> createState() => _ExploreScreenState();
}

class _ExploreScreenState extends State<ExploreScreen> {
  // View state
  bool _isMapView = true;
  String _selectedCategory = 'All Categories';
  String _searchQuery = '';
  Timer? _searchTimer;
  
  // Map controller
  final MapController _mapController = MapController();
  
  // Text controller for search
  final TextEditingController _searchController = TextEditingController();
  
  // Bottom nav index
  int _currentNavIndex = 1; // Explore is active
  
  // Draggable sheet controller
  final DraggableScrollableController _sheetController = DraggableScrollableController();

  // Hardcoded Lahore sample data
  final List<CivicComplaint> _allComplaints = [
    CivicComplaint(
      id: 'complaint_001',
      referenceId: '#LHR-9921',
      title: 'Deep Pothole',
      description: 'Large pothole causing traffic hazards on main road',
      category: 'POTHOLE',
      priority: 'CRITICAL',
      location: 'Gulberg III',
      address: 'Gulberg III • Main Boulevard',
      latitude: 31.5105,
      longitude: 74.3436,
      reportedDate: DateTime.now().subtract(const Duration(hours: 12)),
      status: 'CRITICAL',
      timeAgo: '12m ago',
      region: 'LAHORE',
      isPriority: true,
    ),
    CivicComplaint(
      id: 'complaint_002',
      referenceId: '#LHR-0421',
      title: 'Overflowing Bin',
      description: 'Trash overflowing from garbage bin near market',
      category: 'GARBAGE',
      priority: 'PENDING',
      location: 'Liberty Market',
      address: 'Liberty Market • Main Chowk',
      latitude: 31.5127,
      longitude: 74.3408,
      reportedDate: DateTime.now().subtract(const Duration(hours: 5)),
      status: 'PENDING',
      timeAgo: '5h ago',
      region: 'LAHORE',
      isPriority: false,
    ),
    CivicComplaint(
      id: 'complaint_003',
      referenceId: '#LHR-8845',
      title: 'Road Damage',
      description: 'Multiple potholes on main avenue causing traffic hazard',
      category: 'POTHOLE',
      priority: 'CRITICAL',
      location: 'DHA Phase 5',
      address: 'DHA Phase 5 • Sector C',
      latitude: 31.4697,
      longitude: 74.4023,
      reportedDate: DateTime.now().subtract(const Duration(days: 1)),
      status: 'CRITICAL',
      timeAgo: '1d ago',
      region: 'LAHORE',
      isPriority: true,
    ),
    CivicComplaint(
      id: 'complaint_004',
      referenceId: '#LHR-7632',
      title: 'Litter Accumulation',
      description: 'Excessive litter on sidewalk near shops',
      category: 'GARBAGE',
      priority: 'RESOLVED',
      location: 'Model Town',
      address: 'Model Town • Block C',
      latitude: 31.4833,
      longitude: 74.3167,
      reportedDate: DateTime.now().subtract(const Duration(days: 2)),
      status: 'RESOLVED',
      timeAgo: '2d ago',
      region: 'LAHORE',
      isPriority: false,
    ),
    CivicComplaint(
      id: 'complaint_005',
      referenceId: '#LHR-1122',
      title: 'Street Crack',
      description: 'Large crack forming on main road near school',
      category: 'POTHOLE',
      priority: 'PENDING',
      location: 'Johar Town',
      address: 'Johar Town • Block G',
      latitude: 31.4697,
      longitude: 74.2711,
      reportedDate: DateTime.now().subtract(const Duration(hours: 8)),
      status: 'PENDING',
      timeAgo: '8h ago',
      region: 'LAHORE',
      isPriority: false,
    ),
    CivicComplaint(
      id: 'complaint_006',
      referenceId: '#LHR-3344',
      title: 'Dumped Waste',
      description: 'Illegal dumping of construction waste near residential area',
      category: 'GARBAGE',
      priority: 'CRITICAL',
      location: 'Bahria Town',
      address: 'Bahria Town • Sector E',
      latitude: 31.3685,
      longitude: 74.1803,
      reportedDate: DateTime.now().subtract(const Duration(hours: 3)),
      status: 'CRITICAL',
      timeAgo: '3h ago',
      region: 'LAHORE',
      isPriority: true,
    ),
    CivicComplaint(
      id: 'complaint_007',
      referenceId: '#LHR-5566',
      title: 'Sewage Overflow',
      description: 'Sewage blocking road near hospital',
      category: 'GARBAGE',
      priority: 'CRITICAL',
      location: 'Faisal Town',
      address: 'Faisal Town • Block A',
      latitude: 31.5000,
      longitude: 74.3100,
      reportedDate: DateTime.now().subtract(const Duration(hours: 2)),
      status: 'CRITICAL',
      timeAgo: '2h ago',
      region: 'LAHORE',
      isPriority: true,
    ),
    CivicComplaint(
      id: 'complaint_008',
      referenceId: '#LHR-7788',
      title: 'Broken Road',
      description: 'Road severely damaged after rain',
      category: 'POTHOLE',
      priority: 'PENDING',
      location: 'Garden Town',
      address: 'Garden Town • Main Road',
      latitude: 31.5120,
      longitude: 74.3200,
      reportedDate: DateTime.now().subtract(const Duration(hours: 6)),
      status: 'PENDING',
      timeAgo: '6h ago',
      region: 'LAHORE',
      isPriority: false,
    ),
  ];

  // Stats computed from complaints
  int get _criticalCount => _filteredComplaints.where((c) => c.status == 'CRITICAL').length;
  int get _pendingCount => _filteredComplaints.where((c) => c.status == 'PENDING').length;
  int get _resolvedCount => _filteredComplaints.where((c) => c.status == 'RESOLVED').length;

  List<CivicComplaint> get _filteredComplaints {
    var results = _searchComplaints(_searchQuery);
    
    if (_selectedCategory != 'All Categories') {
      results = results.where((c) => c.category == _selectedCategory).toList();
    }
    
    // Sort: CRITICAL > PENDING > RESOLVED, then by date
    results.sort((a, b) {
      const priorityOrder = {'CRITICAL': 0, 'PENDING': 1, 'RESOLVED': 2};
      final priorityCompare = priorityOrder[a.status]!.compareTo(priorityOrder[b.status]!);
      
      if (priorityCompare != 0) return priorityCompare;
      return b.reportedDate.compareTo(a.reportedDate);
    });
    
    return results;
  }

  List<CivicComplaint> _searchComplaints(String query) {
    if (query.isEmpty) return _allComplaints;
    
    query = query.toLowerCase();
    return _allComplaints.where((complaint) {
      return complaint.location.toLowerCase().contains(query) ||
             complaint.referenceId.toLowerCase().contains(query) ||
             complaint.title.toLowerCase().contains(query) ||
             complaint.address.toLowerCase().contains(query);
    }).toList();
  }

  void _handleSearch(String query) {
    _searchTimer?.cancel();
    _searchTimer = Timer(const Duration(milliseconds: 300), () {
      setState(() {
        _searchQuery = query;
      });
      
      // If results exist, animate to first result and expand panel
      if (_filteredComplaints.isNotEmpty) {
        final first = _filteredComplaints.first;
        _mapController.move(LatLng(first.latitude, first.longitude), 15);
        
        // Expand the bottom sheet to show results
        if (_sheetController.isAttached) {
          _sheetController.animateTo(
            0.5,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      }
    });
  }

  @override
  void dispose() {
    _searchTimer?.cancel();
    _searchController.dispose();
    _sheetController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ExploreColors.backgroundColor,
      drawer: _buildDrawer(),
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            _buildSearchBar(),
            _buildViewToggle(),
            Expanded(
              child: _isMapView ? _buildMapViewWithSheet() : _buildListView(),
            ),
          ],
        ),
      ),
      floatingActionButton: _buildFAB(),
      bottomNavigationBar: _buildBottomNavBar(),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Center(
        child: Text(
          'Regional Map',
          style: GoogleFonts.poppins(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: ExploreColors.textPrimary,
          ),
        ),
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: TextField(
          controller: _searchController,
          onChanged: _handleSearch,
          style: GoogleFonts.roboto(
            fontSize: 15,
            color: ExploreColors.textPrimary, // Fixed: text color now visible
          ),
          decoration: InputDecoration(
            hintText: 'Search area or incident ID (e.g., Gulberg, DHA)',
            hintStyle: GoogleFonts.roboto(
              fontSize: 14,
              color: ExploreColors.textSecondary,
            ),
            prefixIcon: const Icon(Icons.search, color: ExploreColors.textSecondary),
            border: InputBorder.none,
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          ),
        ),
      ),
    );
  }

  Widget _buildViewToggle() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(25),
          border: Border.all(color: ExploreColors.borderLight),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildToggleButton('🗺 Map', true),
            _buildToggleButton('☰ List', false),
          ],
        ),
      ),
    );
  }

  Widget _buildToggleButton(String label, bool isMapButton) {
    final isSelected = _isMapView == isMapButton;
    return GestureDetector(
      onTap: () => setState(() => _isMapView = isMapButton),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? ExploreColors.primaryOrange : Colors.transparent,
          borderRadius: BorderRadius.circular(25),
        ),
        child: Text(
          label,
          style: GoogleFonts.roboto(
            fontSize: 14,
            fontWeight: FontWeight.w500,
            color: isSelected ? Colors.white : ExploreColors.textSecondary,
          ),
        ),
      ),
    );
  }

  Widget _buildMapViewWithSheet() {
    return Stack(
      children: [
        // Map - takes full space
        FlutterMap(
          mapController: _mapController,
          options: MapOptions(
            initialCenter: const LatLng(31.5204, 74.3587), // Lahore center
            initialZoom: 12,
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.streetlight.app',
            ),
            MarkerLayer(
              markers: _buildMapMarkers(),
            ),
          ],
        ),
        // Zoom controls
        Positioned(
          right: 16,
          top: 16,
          child: Column(
            children: [
              _buildZoomButton(Icons.add, () {
                _mapController.move(
                  _mapController.camera.center,
                  _mapController.camera.zoom + 1,
                );
              }),
              const SizedBox(height: 8),
              _buildZoomButton(Icons.remove, () {
                _mapController.move(
                  _mapController.camera.center,
                  _mapController.camera.zoom - 1,
                );
              }),
            ],
          ),
        ),
        // Draggable bottom sheet for issues list
        DraggableScrollableSheet(
          controller: _sheetController,
          initialChildSize: 0.15,
          minChildSize: 0.15,
          maxChildSize: 0.85,
          builder: (context, scrollController) {
            return Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: ListView(
                controller: scrollController,
                padding: EdgeInsets.zero,
                children: [
                  // Drag handle
                  Center(
                    child: Container(
                      margin: const EdgeInsets.only(top: 12, bottom: 8),
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: ExploreColors.borderLight,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  // Header with stats
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Issues in Lahore',
                          style: GoogleFonts.poppins(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            color: ExploreColors.textPrimary,
                          ),
                        ),
                        Text(
                          '${_filteredComplaints.length} found',
                          style: GoogleFonts.roboto(
                            fontSize: 13,
                            color: ExploreColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Stats row
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Row(
                      children: [
                        _buildMiniStat('CRITICAL', _criticalCount, ExploreColors.primaryOrange),
                        const SizedBox(width: 16),
                        _buildMiniStat('PENDING', _pendingCount, ExploreColors.pendingGray),
                        const SizedBox(width: 16),
                        _buildMiniStat('RESOLVED', _resolvedCount, ExploreColors.resolvedGreen),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  // Category filters
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: [
                          _buildCategoryChip('All Categories'),
                          const SizedBox(width: 8),
                          _buildCategoryChip('Potholes', categoryValue: 'POTHOLE'),
                          const SizedBox(width: 8),
                          _buildCategoryChip('Garbage', categoryValue: 'GARBAGE'),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  // Complaints list
                  ..._filteredComplaints.map((complaint) {
                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                      child: _buildComplaintCard(complaint),
                    );
                  }),
                  const SizedBox(height: 80),
                ],
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildMiniStat(String label, int count, Color color) {
    return Row(
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 4),
        Text(
          '$count $label',
          style: GoogleFonts.roboto(
            fontSize: 11,
            fontWeight: FontWeight.w500,
            color: color,
          ),
        ),
      ],
    );
  }

  List<Marker> _buildMapMarkers() {
    return _filteredComplaints.map((complaint) {
      final isPothole = complaint.category == 'POTHOLE';
      final isCritical = complaint.status == 'CRITICAL';
      
      return Marker(
        point: LatLng(complaint.latitude, complaint.longitude),
        width: 50,
        height: 50,
        child: GestureDetector(
          onTap: () => _showComplaintDetail(complaint),
          child: Stack(
            alignment: Alignment.center,
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: isPothole ? ExploreColors.potholeOrange : ExploreColors.garbageGray,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.2),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Icon(
                  isPothole ? Icons.warning_amber_rounded : Icons.delete_outline,
                  color: Colors.white,
                  size: 22,
                ),
              ),
              if (isCritical)
                Positioned(
                  top: 0,
                  right: 0,
                  child: Container(
                    width: 14,
                    height: 14,
                    decoration: BoxDecoration(
                      color: ExploreColors.criticalRed,
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 2),
                    ),
                  ),
                ),
            ],
          ),
        ),
      );
    }).toList();
  }

  Widget _buildZoomButton(IconData icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Icon(icon, color: ExploreColors.textPrimary),
      ),
    );
  }

  Widget _buildListView() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 8),
          _buildRegionalInsightsSection(),
        ],
      ),
    );
  }

  Widget _buildRegionalInsightsSection() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Regional Insights - Lahore',
            style: GoogleFonts.poppins(
              fontSize: 20,
              fontWeight: FontWeight.w600,
              color: ExploreColors.textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          _buildStatsCards(),
          const SizedBox(height: 20),
          _buildCategoryFiltersRow(),
          const SizedBox(height: 16),
          _buildComplaintList(),
          const SizedBox(height: 80), // Space for FAB
        ],
      ),
    );
  }

  Widget _buildStatsCards() {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'CRITICAL',
            _criticalCount.toString(),
            ExploreColors.primaryOrange,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'PENDING',
            _pendingCount.toString(),
            ExploreColors.pendingGray,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'RESOLVED',
            _resolvedCount.toString(),
            ExploreColors.resolvedGreen,
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(String label, String count, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: ExploreColors.borderLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: GoogleFonts.roboto(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: color,
              letterSpacing: 0.5,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            count,
            style: GoogleFonts.poppins(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryFiltersRow() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _buildCategoryChip('All Categories'),
          const SizedBox(width: 8),
          _buildCategoryChip('Potholes', categoryValue: 'POTHOLE'),
          const SizedBox(width: 8),
          _buildCategoryChip('Garbage', categoryValue: 'GARBAGE'),
        ],
      ),
    );
  }

  Widget _buildCategoryChip(String label, {String? categoryValue}) {
    final value = categoryValue ?? label;
    final isSelected = _selectedCategory == value;
    
    return GestureDetector(
      onTap: () => setState(() => _selectedCategory = value),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? ExploreColors.primaryOrange : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? ExploreColors.primaryOrange : ExploreColors.borderLight,
          ),
        ),
        child: Text(
          label,
          style: GoogleFonts.roboto(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: isSelected ? Colors.white : ExploreColors.textSecondary,
          ),
        ),
      ),
    );
  }

  Widget _buildComplaintList() {
    return Column(
      children: _filteredComplaints.map((complaint) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: _buildComplaintCard(complaint),
        );
      }).toList(),
    );
  }

  Widget _buildComplaintCard(CivicComplaint complaint) {
    final isPothole = complaint.category == 'POTHOLE';
    
    return GestureDetector(
      onTap: () {
        // Center map on this complaint
        _mapController.move(LatLng(complaint.latitude, complaint.longitude), 16);
        _showComplaintDetail(complaint);
      },
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: ExploreColors.borderLight),
        ),
        child: Row(
          children: [
            // Category icon
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: isPothole 
                    ? ExploreColors.potholeOrange.withOpacity(0.1) 
                    : ExploreColors.garbageGray.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                isPothole ? Icons.warning_amber_rounded : Icons.delete_outline,
                color: isPothole ? ExploreColors.potholeOrange : ExploreColors.garbageGray,
                size: 24,
              ),
            ),
            const SizedBox(width: 12),
            // Title and address
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    complaint.title,
                    style: GoogleFonts.poppins(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: ExploreColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    complaint.address,
                    style: GoogleFonts.roboto(
                      fontSize: 13,
                      color: ExploreColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            // Status and time
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                _buildStatusBadge(complaint.status),
                const SizedBox(height: 4),
                Text(
                  complaint.timeAgo,
                  style: GoogleFonts.roboto(
                    fontSize: 12,
                    color: ExploreColors.textSecondary,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    Color color;
    switch (status) {
      case 'CRITICAL':
        color = ExploreColors.primaryOrange;
        break;
      case 'PENDING':
        color = ExploreColors.pendingGray;
        break;
      case 'RESOLVED':
        color = ExploreColors.resolvedGreen;
        break;
      default:
        color = ExploreColors.textSecondary;
    }
    
    return Text(
      status,
      style: GoogleFonts.roboto(
        fontSize: 11,
        fontWeight: FontWeight.w700,
        color: color,
        letterSpacing: 0.5,
      ),
    );
  }

  void _showComplaintDetail(CivicComplaint complaint) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    complaint.title,
                    style: GoogleFonts.poppins(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: ExploreColors.textPrimary,
                    ),
                  ),
                ),
                _buildStatusBadge(complaint.status),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              complaint.referenceId,
              style: GoogleFonts.roboto(
                fontSize: 14,
                color: ExploreColors.primaryOrange,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                const Icon(Icons.location_on, size: 18, color: ExploreColors.textSecondary),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    complaint.address,
                    style: GoogleFonts.roboto(
                      fontSize: 14,
                      color: ExploreColors.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              complaint.description,
              style: GoogleFonts.roboto(
                fontSize: 14,
                color: ExploreColors.textPrimary,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => Navigator.pop(context),
                style: ElevatedButton.styleFrom(
                  backgroundColor: ExploreColors.primaryOrange,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  'Close',
                  style: GoogleFonts.roboto(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildDrawer() {
    return Drawer(
      child: Container(
        color: ExploreColors.backgroundColor,
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(
                color: ExploreColors.primaryOrange,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Text(
                    'StreetLight',
                    style: GoogleFonts.poppins(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Urban Management',
                    style: GoogleFonts.roboto(
                      fontSize: 14,
                      color: Colors.white70,
                    ),
                  ),
                ],
              ),
            ),
            ListTile(
              leading: const Icon(Icons.home_outlined),
              title: Text('Home', style: GoogleFonts.roboto()),
              onTap: () {
                Navigator.pop(context);
                Navigator.pushReplacementNamed(context, '/home');
              },
            ),
            ListTile(
              leading: const Icon(Icons.explore, color: ExploreColors.primaryOrange),
              title: Text('Explore', style: GoogleFonts.roboto(color: ExploreColors.primaryOrange)),
              selected: true,
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.person_outline),
              title: Text('Profile', style: GoogleFonts.roboto()),
              onTap: () {
                Navigator.pop(context);
                Navigator.pushReplacementNamed(context, '/profile');
              },
            ),
            ListTile(
              leading: const Icon(Icons.report_outlined),
              title: Text('Report Issue', style: GoogleFonts.roboto()),
              onTap: () {
                Navigator.pop(context);
                Navigator.pushNamed(context, '/report_issue');
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFAB() {
    return FloatingActionButton(
      onPressed: () => Navigator.pushNamed(context, '/report_issue'),
      backgroundColor: ExploreColors.primaryOrange,
      child: const Icon(Icons.add, color: Colors.white, size: 28),
    );
  }

  Widget _buildBottomNavBar() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(Icons.home_outlined, 'HOME', 0, '/home'),
              _buildNavItem(Icons.explore, 'EXPLORE', 1, null),
              _buildNavItem(Icons.person_outline, 'PROFILE', 2, '/profile'),
              _buildNavItem(Icons.warning_amber_outlined, 'ISSUES', 3, '/report_issue'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label, int index, String? route) {
    final isActive = index == _currentNavIndex;
    
    return GestureDetector(
      onTap: () {
        if (route != null && index != _currentNavIndex) {
          Navigator.pushReplacementNamed(context, route);
        }
        setState(() => _currentNavIndex = index);
      },
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: isActive ? ExploreColors.primaryOrange : ExploreColors.textSecondary,
            size: 24,
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: GoogleFonts.roboto(
              fontSize: 10,
              fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
              color: isActive ? ExploreColors.primaryOrange : ExploreColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}

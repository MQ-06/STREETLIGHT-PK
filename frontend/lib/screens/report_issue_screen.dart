// lib/screens/report_issue_screen.dart
import 'dart:async';
import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:http/http.dart' as http;
import '../models/report_issue_data.dart';
import '../services/api_service.dart';
import '../services/user_session.dart';
import '../widgets/app_toast.dart';

class ReportIssueColors {
  static const backgroundColor = Color(0xFFFFF8E7);
  static const primaryOrange = Color(0xFFC85A3A);
  static const submitBrown = Color(0xFFA0522D);
  static const borderTan = Color(0xFFD4C5B9);
  static const textPrimary = Color(0xFF333333);
  static const textSecondary = Color(0xFF888888);
  static const uploadBoxBg = Color(0xFFF5E6F0);
  static const progressGray = Color(0xFFE0E0E0);
  static const successGreen = Color(0xFF4CAF50);
  static const errorRed = Color(0xFFE53935);
  static const headerSubtitle = Color(0xFFB5A89A);
}

class ReportIssueScreen extends StatefulWidget {
  const ReportIssueScreen({super.key});

  @override
  State<ReportIssueScreen> createState() => _ReportIssueScreenState();
}

class _ReportIssueScreenState extends State<ReportIssueScreen> {
  File? _selectedImage;
  LocationData? _currentLocation;
  final TextEditingController _descriptionController = TextEditingController();

  bool _isLoadingLocation = false;
  bool _isLoadingImage = false;
  bool _isSubmitting = false;
  int _currentNavIndex = 3;

  final ImagePicker _imagePicker = ImagePicker();

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  // ─────────────────────────────────────────────
  // LOCATION
  // ─────────────────────────────────────────────

  Future<void> _fetchInitialLocation() async {
    setState(() => _isLoadingLocation = true);
    try {
      final response = await http
          .get(Uri.parse('https://ipapi.co/json/'))
          .timeout(const Duration(seconds: 10));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _currentLocation = LocationData(
            latitude: data['latitude']?.toDouble() ?? 0.0,
            longitude: data['longitude']?.toDouble() ?? 0.0,
            address: '${data['city'] ?? 'Unknown'} Area',
            city: data['city'] ?? 'Unknown',
            state: data['region'] ?? 'Unknown',
            zipCode: data['postal'] ?? '',
          );
        });
      }
    } catch (e) {
      debugPrint('IP geolocation failed: $e');
    } finally {
      setState(() => _isLoadingLocation = false);
    }
  }

  Future<void> _getPreciseLocation() async {
    setState(() => _isLoadingLocation = true);
    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          _showError('Location permission denied');
          return;
        }
      }
      if (permission == LocationPermission.deniedForever) {
        _showError('Location permission permanently denied. Please enable in settings.');
        await openAppSettings();
        return;
      }
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        _showError('Location is off. Opening settings...');
        await Geolocator.openLocationSettings();
        return;
      }
      Position position;
      try {
        position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.medium,
          timeLimit: const Duration(seconds: 15),
        );
      } on TimeoutException {
        _showError('Location timed out. Try again outdoors or near a window.');
        return;
      } catch (e) {
        _showError('Location error: $e');
        return;
      }
      try {
        final placemarks = await placemarkFromCoordinates(
            position.latitude, position.longitude);
        if (placemarks.isNotEmpty) {
          final place = placemarks.first;
          setState(() {
            _currentLocation = LocationData(
              latitude: position.latitude,
              longitude: position.longitude,
              address:
                  '${place.street ?? ''}, ${place.subLocality ?? place.locality ?? ''}',
              city: place.locality ?? 'Unknown',
              state: place.administrativeArea ?? 'Unknown',
              zipCode: place.postalCode ?? '',
            );
          });
        }
      } catch (e) {
        setState(() {
          _currentLocation = LocationData(
            latitude: position.latitude,
            longitude: position.longitude,
            address:
                'Lat: ${position.latitude.toStringAsFixed(4)}, Lng: ${position.longitude.toStringAsFixed(4)}',
            city: 'Unknown',
            state: 'Unknown',
            zipCode: '',
          );
        });
      }
    } catch (e) {
      _showError('Failed to get location: $e');
    } finally {
      setState(() => _isLoadingLocation = false);
    }
  }

  // ─────────────────────────────────────────────
  // IMAGE PICKER — UI completely unchanged
  // ─────────────────────────────────────────────

  Future<void> _pickImage() async {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Select Image Source',
                  style: GoogleFonts.poppins(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: ReportIssueColors.textPrimary)),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildImageSourceOption(
                      icon: Icons.camera_alt,
                      label: 'Camera',
                      onTap: () => _captureImage(ImageSource.camera)),
                  _buildImageSourceOption(
                      icon: Icons.photo_library,
                      label: 'Gallery',
                      onTap: () => _captureImage(ImageSource.gallery)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImageSourceOption({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        decoration: BoxDecoration(
            color: ReportIssueColors.uploadBoxBg,
            borderRadius: BorderRadius.circular(12)),
        child: Column(
          children: [
            Icon(icon, size: 40, color: ReportIssueColors.primaryOrange),
            const SizedBox(height: 8),
            Text(label,
                style: GoogleFonts.roboto(
                    fontSize: 14, color: ReportIssueColors.textPrimary)),
          ],
        ),
      ),
    );
  }

  Future<void> _captureImage(ImageSource source) async {
    Navigator.pop(context);
    setState(() => _isLoadingImage = true);
    try {
      PermissionStatus status;
      if (source == ImageSource.camera) {
        status = await Permission.camera.request();
      } else {
        status = await Permission.photos.request();
      }
      if (status.isDenied) {
        _showError(
            '${source == ImageSource.camera ? 'Camera' : 'Photo'} permission denied');
        return;
      }
      if (status.isPermanentlyDenied) {
        _showError('Permission permanently denied. Please enable in settings.');
        await openAppSettings();
        return;
      }
      final XFile? pickedFile = await _imagePicker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );
      if (pickedFile != null) {
        setState(() => _selectedImage = File(pickedFile.path));
      }
    } catch (e) {
      _showError('Failed to pick image: $e');
    } finally {
      setState(() => _isLoadingImage = false);
    }
  }

  void _showError(String message) {
    if (!mounted) return;
    showAppToast(context, message: message, isError: true);
  }

  // ─────────────────────────────────────────────
  // SUBMIT — calls real API, image stays local
  // ─────────────────────────────────────────────

  Future<void> _submitReport() async {
    // Validation
    if (_selectedImage == null) {
      _showError('Please capture or upload an image');
      return;
    }
    if (_currentLocation == null) {
      _showError('Please enable location access');
      return;
    }

    setState(() => _isSubmitting = true);

    // Auto-generate title from city (AI will detect category)
    final city = _currentLocation!.city;
    final autoTitle = 'Civic Issue in $city';

    // Call API WITH IMAGE — AI Agent will process it and detect category
    final result = await ApiService.createReport(
      imagePath: _selectedImage!.path,  // AI will automatically detect pothole or garbage
      title: autoTitle,
      description: _descriptionController.text.trim(),
      locationAddress: _currentLocation!.address,
      locationCity: _currentLocation!.city,
      locationLat: _currentLocation!.latitude,
      locationLng: _currentLocation!.longitude,
    );

    if (!mounted) return;
    setState(() => _isSubmitting = false);

    if (result['success'] == true) {
      await UserSession.incrementTotalReported();

      showAppToast(context,
          message: 'Report submitted successfully!',
          isError: false,
          duration: const Duration(seconds: 2));

      // Wait a beat then pop back — pass true so HomeScreen refreshes feed
      await Future.delayed(const Duration(milliseconds: 1200));
      if (mounted) Navigator.pop(context, true);
    } else {
      // Show "Invalid Report" with basic error message
      String errorMsg = 'Invalid Report';
      
      // Get the basic reason from AI Agent
      if (result['errors'] != null && result['errors'].isNotEmpty) {
        // Extract simple reason from AI error
        String aiError = result['errors'][0];
        
        // Simplify common AI errors for users
        if (aiError.contains('blurry') || aiError.contains('blur')) {
          errorMsg = 'Invalid Report: Image is too blurry';
        } else if (aiError.contains('dark') || aiError.contains('brightness')) {
          errorMsg = 'Invalid Report: Image is too dark';
        } else if (aiError.contains('bright')) {
          errorMsg = 'Invalid Report: Image is too bright';
        } else if (aiError.contains('resolution') || aiError.contains('Resolution')) {
          errorMsg = 'Invalid Report: Image quality is too low';
        } else if (aiError.contains('GPS') || aiError.contains('location')) {
          errorMsg = 'Invalid Report: GPS location issue';
        } else {
          errorMsg = 'Invalid Report: Please check image quality';
        }
      } else if (result['error'] != null) {
        String error = result['error'].toString();
        if (error.contains('confidence') || error.contains('not clearly visible')) {
          errorMsg = 'Invalid Report: Issue not clearly visible';
        } else if (error.contains('not a civic issue')) {
          errorMsg = 'Invalid Report: Not a valid civic issue';
        } else {
          errorMsg = 'Invalid Report: $error';
        }
      }
      
      _showError(errorMsg);
    }
  }

  // ─────────────────────────────────────────────
  // BUILD
  // ─────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ReportIssueColors.backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            _buildProgressIndicator(),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 16),
                    _buildImageUploadSection(),
                    const SizedBox(height: 24),
                    _buildLocationSection(),
                    const SizedBox(height: 24),
                    _buildDescriptionSection(),
                    const SizedBox(height: 24),
                    _buildSubmitButton(),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: _buildBottomNavBar(),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          IconButton(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back_ios,
                color: ReportIssueColors.textPrimary, size: 20),
          ),
          const Spacer(),
          Column(
            children: [
              Text('Report Issue',
                  style: GoogleFonts.poppins(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: ReportIssueColors.textPrimary)),
              Text('STEP 2 OF 3',
                  style: GoogleFonts.roboto(
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                      color: ReportIssueColors.headerSubtitle,
                      letterSpacing: 1)),
            ],
          ),
          const Spacer(),
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
                color: ReportIssueColors.primaryOrange, shape: BoxShape.circle),
            child: IconButton(
              padding: EdgeInsets.zero,
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: Text('Help',
                        style: GoogleFonts.poppins(fontWeight: FontWeight.w600)),
                    content: Text(
                      '1. Upload a photo of the issue\n'
                      '2. Tap the map to get your location\n'
                      '3. Select the issue category\n'
                      '4. Describe the problem (optional)\n\n'
                      'Then tap Submit.',
                      style: GoogleFonts.roboto(),
                    ),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: Text('Got it',
                            style: TextStyle(
                                color: ReportIssueColors.primaryOrange)),
                      ),
                    ],
                  ),
                );
              },
              icon: const Icon(Icons.question_mark,
                  color: Colors.white, size: 18),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgressIndicator() {
    int filled = 0;
    if (_selectedImage != null) filled = 1;
    if (_selectedImage != null && _currentLocation != null) filled = 2;
    if (_selectedImage != null && _currentLocation != null) filled = 3;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 120, vertical: 8),
      child: Row(
        children: List.generate(3, (i) {
          return Expanded(
            child: Container(
              height: 4,
              margin: EdgeInsets.only(right: i < 2 ? 8 : 0),
              decoration: BoxDecoration(
                color: filled > i
                    ? ReportIssueColors.primaryOrange
                    : ReportIssueColors.progressGray,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          );
        }),
      ),
    );
  }

  // Image upload section
  Widget _buildImageUploadSection() {
    return GestureDetector(
      onTap: _isLoadingImage ? null : _pickImage,
      child: Container(
        width: double.infinity,
        height: 180,
        decoration: BoxDecoration(
          color: ReportIssueColors.uploadBoxBg.withOpacity(0.5),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
              color: ReportIssueColors.borderTan,
              width: 2,
              style: BorderStyle.solid),
        ),
        child: _selectedImage != null
            ? ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    Image.file(_selectedImage!, fit: BoxFit.cover),
                    Positioned(
                      top: 8,
                      right: 8,
                      child: GestureDetector(
                        onTap: () => setState(() => _selectedImage = null),
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: BoxDecoration(
                              color: Colors.black.withOpacity(0.6),
                              shape: BoxShape.circle),
                          child: const Icon(Icons.close,
                              color: Colors.white, size: 18),
                        ),
                      ),
                    ),
                  ],
                ),
              )
            : _isLoadingImage
                ? const Center(
                    child: CircularProgressIndicator(
                        color: ReportIssueColors.primaryOrange))
                : Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        width: 56,
                        height: 56,
                        decoration: BoxDecoration(
                            color: ReportIssueColors.primaryOrange
                                .withOpacity(0.15),
                            shape: BoxShape.circle),
                        child: Stack(
                          alignment: Alignment.center,
                          children: [
                            Icon(Icons.camera_alt,
                                color: ReportIssueColors.primaryOrange,
                                size: 28),
                            Positioned(
                              right: 8,
                              top: 8,
                              child: Container(
                                width: 16,
                                height: 16,
                                decoration: BoxDecoration(
                                    color: ReportIssueColors.primaryOrange,
                                    shape: BoxShape.circle),
                                child: const Icon(Icons.add,
                                    color: Colors.white, size: 12),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text('Capture or Upload Evidence',
                          style: GoogleFonts.roboto(
                              fontSize: 14,
                              color: ReportIssueColors.textSecondary)),
                    ],
                  ),
      ),
    );
  }

  Widget _buildMapPlaceholder() {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [const Color(0xFFF5F0E6), const Color(0xFFE8E4D9)],
        ),
      ),
      child: CustomPaint(
        size: const Size(double.infinity, 140),
        painter: MapGridPainter(),
      ),
    );
  }

  Widget _buildLocationSection() {
    String? staticMapUrl;
    if (_currentLocation != null) {
      final lat = _currentLocation!.latitude;
      final lng = _currentLocation!.longitude;
      staticMapUrl =
          'https://staticmap.openstreetmap.de/staticmap.php?center=$lat,$lng&zoom=14&size=400x200&markers=$lat,$lng,red-pushpin';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('CURRENT LOCATION',
                style: GoogleFonts.roboto(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: ReportIssueColors.textPrimary,
                    letterSpacing: 0.5)),
            if (_currentLocation != null)
              Row(
                children: [
                  const Icon(Icons.check_circle,
                      size: 14, color: ReportIssueColors.successGreen),
                  const SizedBox(width: 4),
                  Text('Located',
                      style: GoogleFonts.roboto(
                          fontSize: 13,
                          color: ReportIssueColors.successGreen,
                          fontWeight: FontWeight.w500)),
                ],
              ),
          ],
        ),
        const SizedBox(height: 12),
        GestureDetector(
          onTap: _isLoadingLocation ? null : _getPreciseLocation,
          child: Container(
            height: 140,
            width: double.infinity,
            decoration: BoxDecoration(
                color: const Color(0xFFE8E4D9),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: ReportIssueColors.borderTan)),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(11),
              child: Stack(
                fit: StackFit.expand,
                children: [
                  if (staticMapUrl != null)
                    Image.network(staticMapUrl,
                        fit: BoxFit.cover,
                        loadingBuilder: (context, child, progress) =>
                            progress == null ? child : _buildMapPlaceholder(),
                        errorBuilder: (_, __, ___) => _buildMapPlaceholder())
                  else
                    _buildMapPlaceholder(),
                  if (_isLoadingLocation)
                    Container(
                      color: Colors.white.withOpacity(0.7),
                      child: const Center(
                        child: CircularProgressIndicator(
                            color: ReportIssueColors.primaryOrange),
                      ),
                    )
                  else if (_currentLocation == null)
                    Container(
                      color: Colors.black.withOpacity(0.1),
                      child: Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.touch_app,
                                color: ReportIssueColors.primaryOrange,
                                size: 36),
                            const SizedBox(height: 8),
                            Text('Tap to get your location',
                                style: GoogleFonts.roboto(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w500,
                                    color: ReportIssueColors.textPrimary)),
                          ],
                        ),
                      ),
                    )
                  else
                    const Center(
                        child: Icon(Icons.location_on,
                            color: Colors.red, size: 40)),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: ReportIssueColors.borderTan)),
          child: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                    color: ReportIssueColors.primaryOrange.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8)),
                child: const Icon(Icons.apartment,
                    color: ReportIssueColors.primaryOrange, size: 22),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _currentLocation?.address ?? 'Fetching location...',
                      style: GoogleFonts.roboto(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                          color: ReportIssueColors.textPrimary),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      _currentLocation != null
                          ? '${_currentLocation!.city}, ${_currentLocation!.state} ${_currentLocation!.zipCode}'
                          : 'Please enable location',
                      style: GoogleFonts.roboto(
                          fontSize: 12,
                          color: ReportIssueColors.textSecondary),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }


  Widget _buildDescriptionSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('DESCRIPTION',
            style: GoogleFonts.roboto(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: ReportIssueColors.textPrimary,
                letterSpacing: 0.5)),
        const SizedBox(height: 12),
        Container(
          decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: ReportIssueColors.borderTan, width: 2)),
          child: TextField(
            controller: _descriptionController,
            maxLines: 5,
            minLines: 4,
            style: GoogleFonts.roboto(
                fontSize: 14, color: ReportIssueColors.textPrimary),
            decoration: InputDecoration(
              hintText: 'Provide specific details (optional)...',
              hintStyle: GoogleFonts.roboto(
                  fontSize: 14,
                  color: ReportIssueColors.textSecondary.withOpacity(0.6)),
              contentPadding: const EdgeInsets.all(16),
              border: InputBorder.none,
            ),
          ),
        ),
      ],
    );
  }

  // Submit button — shows spinner while submitting
  Widget _buildSubmitButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _isSubmitting ? null : _submitReport,
        style: ElevatedButton.styleFrom(
          backgroundColor: ReportIssueColors.submitBrown,
          foregroundColor: Colors.white,
          disabledBackgroundColor:
              ReportIssueColors.submitBrown.withOpacity(0.6),
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          elevation: 0,
        ),
        child: _isSubmitting
            ? const SizedBox(
                height: 22,
                width: 22,
                child: CircularProgressIndicator(
                    color: Colors.white, strokeWidth: 2.5),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('SUBMIT REPORT',
                      style: GoogleFonts.poppins(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 0.5)),
                  const SizedBox(width: 8),
                  const Icon(Icons.arrow_forward, size: 20),
                ],
              ),
      ),
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
              offset: const Offset(0, -2)),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(0, Icons.home, 'Home'),
              _buildNavItem(1, Icons.explore, 'Explore'),
              _buildNavItem(2, Icons.person_outline, 'Profile'),
              _buildNavItem(3, Icons.warning_amber_rounded, 'Issues'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(int index, IconData icon, String label) {
    bool isActive = _currentNavIndex == index;
    return InkWell(
      onTap: () {
        if (index == 0) {
          Navigator.pushReplacementNamed(context, '/home');
        } else if (index == 1) {
          Navigator.pushReplacementNamed(context, '/explore');
        } else if (index == 2) {
          Navigator.pushReplacementNamed(context, '/profile');
        } else {
          setState(() => _currentNavIndex = index);
        }
      },
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon,
                size: 24,
                color: isActive
                    ? ReportIssueColors.primaryOrange
                    : ReportIssueColors.textSecondary),
            const SizedBox(height: 4),
            Text(label,
                style: GoogleFonts.roboto(
                    fontSize: 11,
                    color: isActive
                        ? ReportIssueColors.primaryOrange
                        : ReportIssueColors.textSecondary,
                    fontWeight: isActive ? FontWeight.w600 : FontWeight.normal)),
          ],
        ),
      ),
    );
  }
}

class MapGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFFD4CFC3)
      ..strokeWidth = 0.5
      ..style = PaintingStyle.stroke;
    for (double y = 0; y < size.height; y += 20) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
    for (double x = 0; x < size.width; x += 20) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
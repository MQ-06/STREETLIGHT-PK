// This is a basic Flutter widget test.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:streetlight/main.dart';

void main() {
  testWidgets('Splash screen smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const StreetlightApp());

    // Verify that the app renders
    expect(find.byType(Scaffold), findsOneWidget);
  });
}

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sdh_navigasyon/features/destination/presentation/widgets/zoomable_hospital_map.dart';

void main() {
  testWidgets('supports pinch zoom and double-tap reset', (tester) async {
    final controller = TransformationController();
    addTearDown(controller.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ZoomableHospitalMap(
            assetPath: 'kan_alma_yol_tarifi.png',
            transformationController: controller,
          ),
        ),
      ),
    );

    final viewer = tester.widget<InteractiveViewer>(
      find.byKey(const Key('destination-map-interactive-viewer')),
    );
    expect(viewer.minScale, 1);
    expect(viewer.maxScale, 5);
    expect(viewer.panEnabled, isFalse);
    expect(viewer.scaleEnabled, isTrue);

    final center = tester.getCenter(find.byType(InteractiveViewer));
    final firstFinger = await tester.startGesture(center - const Offset(20, 0));
    final secondFinger = await tester.startGesture(center + const Offset(20, 0));
    await firstFinger.moveTo(center - const Offset(80, 0));
    await secondFinger.moveTo(center + const Offset(80, 0));
    await tester.pump();
    await firstFinger.up();
    await secondFinger.up();
    await tester.pump();

    expect(controller.value.getMaxScaleOnAxis(), greaterThan(1));
    expect(
      tester
          .widget<InteractiveViewer>(find.byType(InteractiveViewer))
          .panEnabled,
      isTrue,
    );

    await tester.tap(find.byType(InteractiveViewer));
    await tester.pump(const Duration(milliseconds: 50));
    await tester.tap(find.byType(InteractiveViewer));
    await tester.pumpAndSettle();

    expect(controller.value, Matrix4.identity());
  });

  testWidgets('double tap zooms toward the tapped area', (tester) async {
    final controller = TransformationController();
    addTearDown(controller.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ZoomableHospitalMap(
            assetPath: 'kan_alma_yol_tarifi.png',
            transformationController: controller,
          ),
        ),
      ),
    );

    await tester.tap(find.byType(InteractiveViewer));
    await tester.pump(const Duration(milliseconds: 50));
    await tester.tap(find.byType(InteractiveViewer));
    await tester.pumpAndSettle();

    expect(controller.value.getMaxScaleOnAxis(), 2.5);
  });
}

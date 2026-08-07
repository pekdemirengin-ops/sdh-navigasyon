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
    expect(viewer.panEnabled, isTrue);
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
    final transformAfterPinch = controller.value.clone();
    final pan = await tester.startGesture(center);
    await pan.moveBy(const Offset(35, 25));
    await tester.pump();
    await pan.up();
    await tester.pump();

    expect(controller.value.storage[12], isNot(transformAfterPinch.storage[12]));
    expect(controller.value.storage[13], isNot(transformAfterPinch.storage[13]));

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

  testWidgets('a two-pointer pinch is not mistaken for a double tap',
      (tester) async {
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

    final center = tester.getCenter(find.byType(InteractiveViewer));
    final first = await tester.startGesture(center - const Offset(25, 0),
        pointer: 1);
    final second = await tester.startGesture(center + const Offset(25, 0),
        pointer: 2);
    await first.moveBy(const Offset(-50, -20));
    await second.moveBy(const Offset(50, 20));
    await tester.pump();
    await first.up();
    await second.up();
    await tester.pump();

    expect(controller.value.getMaxScaleOnAxis(), greaterThan(1));
    expect(controller.value.getMaxScaleOnAxis(), isNot(2.5));
  });
}

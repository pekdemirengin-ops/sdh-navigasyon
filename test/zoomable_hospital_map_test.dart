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
          .widget<InteractiveViewer>(
            find.byKey(const Key('destination-map-interactive-viewer')),
          )
          .panEnabled,
      isTrue,
    );
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
    expect(
      tester
          .widget<InteractiveViewer>(
            find.byKey(const Key('destination-map-interactive-viewer')),
          )
          .panEnabled,
      isFalse,
    );
  });

  testWidgets('parent scroll works before zoom and again after reset',
      (tester) async {
    final controller = TransformationController();
    addTearDown(controller.dispose);
    final scrollController = ScrollController();
    addTearDown(scrollController.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ListView(
            controller: scrollController,
            children: [
              const SizedBox(height: 300),
              SizedBox(
                height: 300,
                child: ZoomableHospitalMap(
                  assetPath: 'kan_alma_yol_tarifi.png',
                  transformationController: controller,
                ),
              ),
              const SizedBox(height: 700),
            ],
          ),
        ),
      ),
    );

    final map = find.byType(InteractiveViewer);
    await tester.drag(map, const Offset(0, -100));
    await tester.pumpAndSettle();
    expect(scrollController.offset, greaterThan(0));

    final center = tester.getCenter(map);
    final first = await tester.startGesture(center - const Offset(20, 0));
    final second = await tester.startGesture(center + const Offset(20, 0));
    await first.moveTo(center - const Offset(70, 0));
    await second.moveTo(center + const Offset(70, 0));
    await tester.pump();
    await first.up();
    await second.up();
    await tester.pump();
    expect(controller.value.getMaxScaleOnAxis(), greaterThan(1));

    final beforeHorizontalPan = controller.value.storage[12];
    await tester.drag(map, const Offset(40, 0));
    await tester.pumpAndSettle();
    expect(controller.value.storage[12], isNot(beforeHorizontalPan));

    final scrollBeforeVerticalPan = scrollController.offset;
    final beforeVerticalPan = controller.value.storage[13];
    await tester.drag(map, const Offset(0, -40));
    await tester.pumpAndSettle();
    expect(controller.value.storage[13], isNot(beforeVerticalPan));
    expect(scrollController.offset, scrollBeforeVerticalPan);

    controller.value = Matrix4.identity();
    await tester.pump();
    expect(controller.value.getMaxScaleOnAxis(), 1);

    await tester.drag(map, const Offset(0, -100));
    await tester.pumpAndSettle();
    expect(scrollController.offset, greaterThan(scrollBeforeVerticalPan));
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

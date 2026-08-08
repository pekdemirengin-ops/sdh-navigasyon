import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sdh_navigasyon/features/destination/presentation/widgets/zoomable_hospital_map.dart';

void main() {
  Finder mapSurface() =>
      find.byKey(const Key('destination-map-gesture-surface'));

  Future<void> pinchOut(
    WidgetTester tester,
    Finder target, {
    double startDistance = 20,
    double endDistance = 80,
  }) async {
    final center = tester.getCenter(target);
    final first = await tester.startGesture(
      center - Offset(startDistance, 0),
      pointer: 1,
    );
    final second = await tester.startGesture(
      center + Offset(startDistance, 0),
      pointer: 2,
    );
    await tester.pump();

    await first.moveTo(center - Offset(endDistance, 0));
    await second.moveTo(center + Offset(endDistance, 0));
    await tester.pump();

    await first.up();
    await second.up();
    await tester.pumpAndSettle();
  }

  testWidgets('two-pointer pinch increases scale', (tester) async {
    final controller = TransformationController();
    addTearDown(controller.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Center(
            child: SizedBox(
              width: 320,
              height: 320,
              child: ZoomableHospitalMap(
                assetPath: 'kan_alma_yol_tarifi.png',
                transformationController: controller,
              ),
            ),
          ),
        ),
      ),
    );

    expect(controller.value.getMaxScaleOnAxis(), 1);
    await pinchOut(tester, mapSurface());
    expect(controller.value.getMaxScaleOnAxis(), greaterThan(1));
    expect(controller.value.getMaxScaleOnAxis(), lessThanOrEqualTo(5));
  });

  testWidgets('one-finger vertical drag scrolls parent at 1x', (tester) async {
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
              const SizedBox(height: 200),
              SizedBox(
                height: 300,
                child: ZoomableHospitalMap(
                  assetPath: 'kan_alma_yol_tarifi.png',
                  transformationController: controller,
                ),
              ),
              const SizedBox(height: 900),
            ],
          ),
        ),
      ),
    );

    expect(controller.value.getMaxScaleOnAxis(), 1);
    await tester.drag(mapSurface(), const Offset(0, -140));
    await tester.pumpAndSettle();

    expect(scrollController.offset, greaterThan(0));
    expect(controller.value, Matrix4.identity());
  });

  testWidgets('zoomed map owns horizontal and vertical one-finger pan',
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
              const SizedBox(height: 100),
              SizedBox(
                height: 320,
                child: ZoomableHospitalMap(
                  assetPath: 'kan_alma_yol_tarifi.png',
                  transformationController: controller,
                ),
              ),
              const SizedBox(height: 900),
            ],
          ),
        ),
      ),
    );

    await pinchOut(tester, mapSurface());
    expect(controller.value.getMaxScaleOnAxis(), greaterThan(1));

    final xBefore = controller.value.storage[12];
    await tester.drag(mapSurface(), const Offset(45, 0));
    await tester.pumpAndSettle();
    expect(controller.value.storage[12], isNot(xBefore));

    final pageBefore = scrollController.offset;
    final yBefore = controller.value.storage[13];
    await tester.drag(mapSurface(), const Offset(0, -45));
    await tester.pumpAndSettle();

    expect(controller.value.storage[13], isNot(yBefore));
    expect(scrollController.offset, pageBefore);
  });

  testWidgets('double tap zooms to 2.5x and second double tap resets',
      (tester) async {
    final controller = TransformationController();
    addTearDown(controller.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 320,
            height: 320,
            child: ZoomableHospitalMap(
              assetPath: 'kan_alma_yol_tarifi.png',
              transformationController: controller,
            ),
          ),
        ),
      ),
    );

    await tester.tap(mapSurface());
    await tester.pump(const Duration(milliseconds: 50));
    await tester.tap(mapSurface());
    await tester.pumpAndSettle();
    expect(controller.value.getMaxScaleOnAxis(), 2.5);

    await tester.tap(mapSurface());
    await tester.pump(const Duration(milliseconds: 50));
    await tester.tap(mapSurface());
    await tester.pumpAndSettle();
    expect(controller.value, Matrix4.identity());
  });

  testWidgets('reset to 1x restores parent vertical scroll', (tester) async {
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
              const SizedBox(height: 200),
              SizedBox(
                height: 300,
                child: ZoomableHospitalMap(
                  assetPath: 'kan_alma_yol_tarifi.png',
                  transformationController: controller,
                ),
              ),
              const SizedBox(height: 900),
            ],
          ),
        ),
      ),
    );

    await pinchOut(tester, mapSurface());
    expect(controller.value.getMaxScaleOnAxis(), greaterThan(1));

    await tester.tap(mapSurface());
    await tester.pump(const Duration(milliseconds: 50));
    await tester.tap(mapSurface());
    await tester.pumpAndSettle();
    expect(controller.value, Matrix4.identity());

    final before = scrollController.offset;
    await tester.drag(mapSurface(), const Offset(0, -140));
    await tester.pumpAndSettle();
    expect(scrollController.offset, greaterThan(before));
  });

  testWidgets('a two-pointer pinch is not mistaken for double tap',
      (tester) async {
    final controller = TransformationController();
    addTearDown(controller.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 320,
            height: 320,
            child: ZoomableHospitalMap(
              assetPath: 'kan_alma_yol_tarifi.png',
              transformationController: controller,
            ),
          ),
        ),
      ),
    );

    await pinchOut(tester, mapSurface());
    final scale = controller.value.getMaxScaleOnAxis();
    expect(scale, greaterThan(1));
    expect(scale, isNot(2.5));
  });
}

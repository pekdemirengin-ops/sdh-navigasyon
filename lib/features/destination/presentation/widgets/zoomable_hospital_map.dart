import 'dart:math' as math;

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

/// Displays a hospital plan without changing its aspect ratio and allows the
/// user to inspect it with touch gestures.
///
/// Gesture ownership is intentionally pointer-aware:
/// - At 1x, a single-finger drag is left to an ancestor [Scrollable].
/// - At 1x, a second pointer immediately claims the gesture for pinch zoom.
/// - Above 1x, a single pointer is claimed immediately for map panning.
class ZoomableHospitalMap extends StatefulWidget {
  const ZoomableHospitalMap({
    required this.assetPath,
    this.transformationController,
    super.key,
  });

  final String assetPath;

  /// Can be supplied by tests or by a parent that needs to observe the zoom.
  final TransformationController? transformationController;

  @override
  State<ZoomableHospitalMap> createState() => _ZoomableHospitalMapState();
}

class _ZoomableHospitalMapState extends State<ZoomableHospitalMap> {
  static const double _minScale = 1;
  static const double _maxScale = 5;
  static const double _doubleTapScale = 2.5;

  // A mild gain makes pinch zoom feel more responsive on physical phones
  // without making small finger movements jumpy or difficult to control.
  static const double _pinchSensitivity = 1.25;

  late TransformationController _controller;
  late bool _isZoomed;

  final Set<int> _activePointers = <int>{};
  Offset? _pointerDownPosition;
  Offset? _lastTapPosition;
  Duration? _lastTapTime;
  int? _tapPointer;
  bool _tapMoved = false;

  double _gestureStartScale = _minScale;
  Offset _gestureStartScenePoint = Offset.zero;

  @override
  void initState() {
    super.initState();
    _controller = widget.transformationController ?? TransformationController();
    _isZoomed = _currentScale > _minScale;
    _controller.addListener(_handleTransformationChanged);
  }

  @override
  void didUpdateWidget(ZoomableHospitalMap oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.transformationController == widget.transformationController) {
      return;
    }

    _controller.removeListener(_handleTransformationChanged);
    if (oldWidget.transformationController == null) {
      _controller.dispose();
    }

    _controller = widget.transformationController ?? TransformationController();
    _isZoomed = _currentScale > _minScale;
    _controller.addListener(_handleTransformationChanged);
  }

  @override
  void dispose() {
    _controller.removeListener(_handleTransformationChanged);
    if (widget.transformationController == null) {
      _controller.dispose();
    }
    super.dispose();
  }

  double get _currentScale => _controller.value.getMaxScaleOnAxis();

  void _handleTransformationChanged() {
    // A small tolerance prevents floating-point noise around identity from
    // accidentally switching ownership of one-finger gestures.
    _isZoomed = _currentScale > _minScale + 0.001;
  }

  void _handleScaleStart(ScaleStartDetails details) {
    _gestureStartScale = _currentScale.clamp(_minScale, _maxScale);
    _gestureStartScenePoint = _controller.toScene(details.localFocalPoint);
  }

  void _handleScaleUpdate(ScaleUpdateDetails details) {
    // At base scale a lone pointer belongs to the surrounding page. The custom
    // recognizer also withholds that pointer from the gesture arena, so this is
    // a defensive guard rather than the primary arbitration mechanism.
    if (!_isZoomed && details.pointerCount < 2) {
      return;
    }

    final responsiveScale = math.pow(details.scale, _pinchSensitivity).toDouble();
    final targetScale = (_gestureStartScale * responsiveScale)
        .clamp(_minScale, _maxScale)
        .toDouble();
    final focalPoint = details.localFocalPoint;

    // Keep the scene point that was under the focal point at gesture start
    // under the current focal point. This handles both pinch zoom and panning
    // with the same transform and preserves the map's aspect ratio.
    final translation = Offset(
      focalPoint.dx - (_gestureStartScenePoint.dx * targetScale),
      focalPoint.dy - (_gestureStartScenePoint.dy * targetScale),
    );

    _controller.value = Matrix4.identity()
      ..translateByDouble(translation.dx, translation.dy, 0.0, 1.0)
      ..scaleByDouble(targetScale, targetScale, targetScale, 1.0);
  }

  void _handleScaleEnd(ScaleEndDetails details) {
    if ((_currentScale - _minScale).abs() <= 0.001) {
      _controller.value = Matrix4.identity();
    }
  }

  void _handlePointerDown(PointerDownEvent event) {
    if (_activePointers.isNotEmpty) {
      // A second simultaneous pointer means this is a scale gesture, not a
      // double tap. Raw pointer tracking does not participate in the arena.
      _tapPointer = null;
      _lastTapTime = null;
    } else {
      _tapPointer = event.pointer;
      _pointerDownPosition = event.localPosition;
      _tapMoved = false;
    }
    _activePointers.add(event.pointer);
  }

  void _handlePointerMove(PointerMoveEvent event) {
    if (event.pointer == _tapPointer &&
        _pointerDownPosition != null &&
        (event.localPosition - _pointerDownPosition!).distance > kTouchSlop) {
      _tapMoved = true;
    }
  }

  void _handlePointerUp(PointerUpEvent event) {
    _activePointers.remove(event.pointer);
    if (event.pointer != _tapPointer || _tapMoved || _activePointers.isNotEmpty) {
      return;
    }

    final previousTime = _lastTapTime;
    final previousPosition = _lastTapPosition;
    final isDoubleTap = previousTime != null &&
        event.timeStamp - previousTime <= kDoubleTapTimeout &&
        previousPosition != null &&
        (event.localPosition - previousPosition).distance <= kDoubleTapSlop;

    if (isDoubleTap) {
      _lastTapTime = null;
      _lastTapPosition = null;
      _handleDoubleTap(event.localPosition);
    } else {
      _lastTapTime = event.timeStamp;
      _lastTapPosition = event.localPosition;
    }
  }

  void _handlePointerCancel(PointerCancelEvent event) {
    _activePointers.remove(event.pointer);
    if (event.pointer == _tapPointer) {
      _tapPointer = null;
    }
  }

  void _handleDoubleTap(Offset position) {
    if (_isZoomed) {
      _controller.value = Matrix4.identity();
      return;
    }

    _controller.value = Matrix4.identity()
 ..translateByDouble(
  position.dx * (1 - _doubleTapScale),
  position.dy * (1 - _doubleTapScale),
  0.0,
  1.0,
)
..scaleByDouble(
  _doubleTapScale,
  _doubleTapScale,
  _doubleTapScale,
  1.0,
);
}
  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: Listener(
        behavior: HitTestBehavior.opaque,
        onPointerDown: _handlePointerDown,
        onPointerMove: _handlePointerMove,
        onPointerUp: _handlePointerUp,
        onPointerCancel: _handlePointerCancel,
        child: RawGestureDetector(
          key: const Key('destination-map-gesture-surface'),
          behavior: HitTestBehavior.opaque,
          gestures: <Type, GestureRecognizerFactory>{
            _PointerAwareScaleGestureRecognizer:
                GestureRecognizerFactoryWithHandlers<
                    _PointerAwareScaleGestureRecognizer>(
              () => _PointerAwareScaleGestureRecognizer(
                debugOwner: this,
                allowSinglePointer: () => _isZoomed,
              ),
              (_PointerAwareScaleGestureRecognizer recognizer) {
                recognizer.allowSinglePointer = () => _isZoomed;
                recognizer.onStart = _handleScaleStart;
                recognizer.onUpdate = _handleScaleUpdate;
                recognizer.onEnd = _handleScaleEnd;
              },
            ),
          },
          child: AnimatedBuilder(
            animation: _controller,
            builder: (context, child) => Transform(
              key: const Key('destination-map-transform'),
              transform: _controller.value,
              alignment: Alignment.topLeft,
              child: child,
            ),
            child: Image.asset(
              widget.assetPath,
              width: double.infinity,
              fit: BoxFit.contain,
              errorBuilder: (_, __, ___) => const SizedBox.shrink(),
            ),
          ),
        ),
      ),
    );
  }
}

/// A scale recognizer that deliberately stays out of the one-pointer gesture
/// arena while the map is at 1x. This lets an ancestor vertical Scrollable win
/// naturally. If a second pointer arrives before the parent wins, the map
/// claims the sequence for pinch zoom. Once zoomed, the first pointer is
/// claimed immediately so horizontal, vertical and diagonal map panning are
/// not stolen by the parent Scrollable.
class _PointerAwareScaleGestureRecognizer extends ScaleGestureRecognizer {
  _PointerAwareScaleGestureRecognizer({
    required this.allowSinglePointer,
    super.debugOwner,
  });

  bool Function() allowSinglePointer;
  final Set<int> _trackedPointers = <int>{};

  @override
  void addAllowedPointer(PointerDownEvent event) {
    _trackedPointers.add(event.pointer);
    super.addAllowedPointer(event);

    if (allowSinglePointer() || _trackedPointers.length >= 2) {
      resolve(GestureDisposition.accepted);
    }
  }

  @override
  void handleEvent(PointerEvent event) {
    // ScaleGestureRecognizer can recognize focal-point motion with a single
    // pointer. Suppress those move events at 1x so it cannot pre-empt the
    // ancestor ListView. Pointer down/up/cancel events are still forwarded so
    // the recognizer's internal state remains consistent and a second pointer
    // can promote the sequence to a pinch.
    if (event is PointerMoveEvent &&
        _trackedPointers.length == 1 &&
        !allowSinglePointer()) {
      return;
    }

    super.handleEvent(event);

    if (event is PointerUpEvent || event is PointerCancelEvent) {
      _trackedPointers.remove(event.pointer);
    }
  }

  @override
  void didStopTrackingLastPointer(int pointer) {
    _trackedPointers.clear();
    super.didStopTrackingLastPointer(pointer);
  }
}

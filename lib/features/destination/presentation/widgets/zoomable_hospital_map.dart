import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

/// Displays a hospital plan without changing its aspect ratio and allows the
/// user to inspect it with native Flutter touch gestures.
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
  static const double _doubleTapScale = 2.5;

  late TransformationController _controller;
  final Set<int> _activePointers = <int>{};
  Offset? _pointerDownPosition;
  Offset? _lastTapPosition;
  Duration? _lastTapTime;
  int? _tapPointer;
  bool _tapMoved = false;

  @override
  void initState() {
    super.initState();
    _controller = widget.transformationController ?? TransformationController();
  }

  @override
  void didUpdateWidget(ZoomableHospitalMap oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.transformationController == widget.transformationController) {
      return;
    }

    if (oldWidget.transformationController == null) {
      _controller.dispose();
    }
    _controller = widget.transformationController ?? TransformationController();
  }

  @override
  void dispose() {
    if (widget.transformationController == null) {
      _controller.dispose();
    }
    super.dispose();
  }

  void _handlePointerDown(PointerDownEvent event) {
    if (_activePointers.isNotEmpty) {
      // A second simultaneous pointer means this is a scale gesture, not a
      // double tap. Listening to raw pointer events keeps us out of Flutter's
      // gesture arena, so InteractiveViewer remains the sole scale/pan owner.
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
    if (_controller.value.getMaxScaleOnAxis() > 1) {
      _controller.value = Matrix4.identity();
      return;
    }

    _controller.value = Matrix4.identity()
      ..translate(
        position.dx * (1 - _doubleTapScale),
        position.dy * (1 - _doubleTapScale),
      )
      ..scale(_doubleTapScale);
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
        child: InteractiveViewer(
          key: const Key('destination-map-interactive-viewer'),
          transformationController: _controller,
          minScale: 1,
          maxScale: 5,
          panEnabled: true,
          scaleEnabled: true,
          child: Image.asset(
            widget.assetPath,
            width: double.infinity,
            fit: BoxFit.contain,
            errorBuilder: (_, __, ___) => const SizedBox.shrink(),
          ),
        ),
      ),
    );
  }
}

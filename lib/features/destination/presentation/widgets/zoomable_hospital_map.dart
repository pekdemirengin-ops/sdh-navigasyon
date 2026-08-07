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
  TapDownDetails? _doubleTapDetails;
  bool _isZoomed = false;

  @override
  void initState() {
    super.initState();
    _controller = widget.transformationController ?? TransformationController();
    _controller.addListener(_handleTransformationChanged);
    _isZoomed = _controller.value.getMaxScaleOnAxis() > 1;
  }

  @override
  void didUpdateWidget(ZoomableHospitalMap oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.transformationController == widget.transformationController) {
      return;
    }

    if (oldWidget.transformationController == null) {
      _controller.removeListener(_handleTransformationChanged);
      _controller.dispose();
    } else {
      _controller.removeListener(_handleTransformationChanged);
    }
    _controller = widget.transformationController ?? TransformationController();
    _controller.addListener(_handleTransformationChanged);
    _isZoomed = _controller.value.getMaxScaleOnAxis() > 1;
  }

  @override
  void dispose() {
    _controller.removeListener(_handleTransformationChanged);
    if (widget.transformationController == null) {
      _controller.dispose();
    }
    super.dispose();
  }

  void _handleTransformationChanged() {
    final isZoomed = _controller.value.getMaxScaleOnAxis() > 1;
    if (isZoomed != _isZoomed) {
      setState(() => _isZoomed = isZoomed);
    }
  }

  void _handleDoubleTap() {
    if (_controller.value.getMaxScaleOnAxis() > 1) {
      _controller.value = Matrix4.identity();
      return;
    }

    final position = _doubleTapDetails?.localPosition ?? Offset.zero;
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
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onDoubleTapDown: (details) => _doubleTapDetails = details,
        onDoubleTap: _handleDoubleTap,
        child: InteractiveViewer(
          key: const Key('destination-map-interactive-viewer'),
          transformationController: _controller,
          minScale: 1,
          maxScale: 5,
          // At the base scale vertical drags remain available to the page's
          // ListView. Once enlarged, one finger moves around the plan.
          panEnabled: _isZoomed,
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

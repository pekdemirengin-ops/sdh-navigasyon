import 'package:flutter/material.dart';

import '../../search/domain/models/search_result.dart';

class DestinationScreen extends StatelessWidget {
  const DestinationScreen({required this.result, super.key});
  final SearchResult result;

  @override
  Widget build(BuildContext context) {
    final unit = result.unit;
    return Scaffold(
      appBar: AppBar(title: Text(unit.name)),
      body: ListView(padding: const EdgeInsets.all(20), children: [
        Chip(avatar: const Icon(Icons.layers_outlined), label: Text(unit.floor)),
        const SizedBox(height: 12),
        Text('Yol tarifi', style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 8),
        Text(unit.directions),
        const SizedBox(height: 20),
        ClipRRect(borderRadius: BorderRadius.circular(16), child: Image.asset(unit.mapAsset, errorBuilder: (_, __, ___) => const SizedBox.shrink())),
      ]),
    );
  }
}

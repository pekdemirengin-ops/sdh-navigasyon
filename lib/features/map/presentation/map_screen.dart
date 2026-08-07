import 'package:flutter/material.dart';
import '../../../core/widgets/app_drawer.dart';

class MapScreen extends StatelessWidget {
  const MapScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Harita')),
        drawer: const AppDrawer(),
        body: const Center(
          child: Text('Bir birim seçtiğinizde ilgili yol krokisi burada gösterilir.'),
        ),
      );
}

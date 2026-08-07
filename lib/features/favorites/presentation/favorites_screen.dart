import 'package:flutter/material.dart';
import '../../../core/widgets/app_drawer.dart';

class FavoritesScreen extends StatelessWidget {
  const FavoritesScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('Favoriler')), drawer: const AppDrawer(), body: const Center(child: Text('Henüz favori biriminiz yok.')));
}

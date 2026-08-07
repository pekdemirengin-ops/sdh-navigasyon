import 'package:flutter/material.dart';
import '../../../core/widgets/app_drawer.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('Ayarlar')), drawer: const AppDrawer(), body: const Center(child: Text('Uygulama ayarları')));
}

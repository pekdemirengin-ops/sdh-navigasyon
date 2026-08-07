import 'package:flutter/material.dart';
import '../../../core/widgets/app_drawer.dart';

class RecentScreen extends StatelessWidget {
  const RecentScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('Son Ziyaretler')), drawer: const AppDrawer(), body: const Center(child: Text('Henüz ziyaret geçmişiniz yok.')));
}

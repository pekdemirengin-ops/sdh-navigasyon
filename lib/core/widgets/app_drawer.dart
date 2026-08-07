import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../router/app_router.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({super.key});

  @override
  Widget build(BuildContext context) => Drawer(
        child: SafeArea(
          child: ListView(children: [
            const ListTile(title: Text('SDH Navigasyon', style: TextStyle(fontWeight: FontWeight.bold))),
            _item(context, Icons.home_outlined, 'Ana sayfa', AppRoutes.home),
            _item(context, Icons.search, 'Birim ara', AppRoutes.search),
            _item(context, Icons.map_outlined, 'Harita', AppRoutes.map),
            _item(context, Icons.favorite_outline, 'Favoriler', AppRoutes.favorites),
            _item(context, Icons.history, 'Son ziyaretler', AppRoutes.recent),
            _item(context, Icons.settings_outlined, 'Ayarlar', AppRoutes.settings),
          ]),
        ),
      );

  Widget _item(BuildContext context, IconData icon, String label, String route) => ListTile(
        leading: Icon(icon),
        title: Text(label),
        onTap: () {
          Navigator.pop(context);
          context.go(route);
        },
      );
}

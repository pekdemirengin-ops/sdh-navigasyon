import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_router.dart';
import '../../../core/widgets/app_drawer.dart';
import '../../search/presentation/providers/search_providers.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final results = ref.watch(searchResultsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('SDH Navigasyon')),
      drawer: const AppDrawer(),
      body: ListView(padding: const EdgeInsets.all(20), children: [
        Text('Nereye gitmek istiyorsunuz?', style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 16),
        TextField(
          readOnly: true,
          onTap: () => context.push(AppRoutes.search),
          decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Poliklinik veya birim ara'),
        ),
        const SizedBox(height: 24),
        Text('Tüm birimler', style: Theme.of(context).textTheme.titleLarge),
        results.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => Text('Birimler yüklenemedi: $error'),
          data: (items) => Column(children: [
            for (final item in items.take(6))
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const CircleAvatar(child: Icon(Icons.local_hospital_outlined)),
                title: Text(item.unit.name),
                subtitle: Text(item.unit.floor),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.push(AppRoutes.destination, extra: item),
              ),
          ]),
        ),
      ]),
    );
  }
}

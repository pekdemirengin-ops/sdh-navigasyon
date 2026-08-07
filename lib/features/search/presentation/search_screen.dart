import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_router.dart';
import 'providers/search_providers.dart';

class SearchScreen extends ConsumerWidget {
  const SearchScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final results = ref.watch(searchResultsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Birim Ara')),
      body: Column(children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: TextField(
            autofocus: true,
            onChanged: (value) => ref.read(searchQueryProvider.notifier).state = value,
            decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Birim adı, kat veya hizmet'),
          ),
        ),
        Expanded(
          child: results.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, _) => Center(child: Text('Arama yapılamadı: $error')),
            data: (items) => items.isEmpty
                ? const Center(child: Text('Eşleşen birim bulunamadı.'))
                : ListView.builder(
                    itemCount: items.length,
                    itemBuilder: (context, index) {
                      final result = items[index];
                      return ListTile(
                        leading: const Icon(Icons.place_outlined),
                        title: Text(result.unit.name),
                        subtitle: Text(result.unit.floor),
                        onTap: () => context.push(AppRoutes.destination, extra: result),
                      );
                    },
                  ),
          ),
        ),
      ]),
    );
  }
}

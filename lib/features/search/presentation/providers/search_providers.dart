import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../destination/data/hospital_unit_repository_impl.dart';
import '../../../destination/domain/repositories/hospital_unit_repository.dart';
import '../../domain/models/search_result.dart';
import '../../domain/services/search_service.dart';

final hospitalUnitRepositoryProvider = Provider<HospitalUnitRepository>(
  (ref) => const HospitalUnitRepositoryImpl(),
);

final searchServiceProvider = Provider<SearchService>(
  (ref) => SearchService(ref.watch(hospitalUnitRepositoryProvider)),
);

final searchQueryProvider = StateProvider.autoDispose<String>((ref) => '');

final searchResultsProvider = FutureProvider.autoDispose<List<SearchResult>>(
  (ref) => ref.watch(searchServiceProvider).search(ref.watch(searchQueryProvider)),
);

import '../../../destination/domain/repositories/hospital_unit_repository.dart';
import '../models/search_result.dart';

class SearchService {
  const SearchService(this._repository);
  final HospitalUnitRepository _repository;

  Future<List<SearchResult>> search(String query) async {
    final normalized = _normalize(query.trim());
    final units = await _repository.getAll();
    if (normalized.isEmpty) {
      return [for (final unit in units) SearchResult(unit: unit, score: 0)];
    }
    final results = <SearchResult>[];
    for (final unit in units) {
      final fields = [unit.name, unit.floor, ...unit.aliases].map(_normalize);
      final score = fields.any((value) => value == normalized)
          ? 2
          : fields.any((value) => value.contains(normalized))
              ? 1
              : 0;
      if (score > 0) results.add(SearchResult(unit: unit, score: score));
    }
    results.sort((a, b) => b.score.compareTo(a.score));
    return results;
  }

  String _normalize(String value) => value.toLowerCase().replaceAll('ı', 'i');
}

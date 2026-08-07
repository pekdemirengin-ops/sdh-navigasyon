import '../../../destination/domain/models/hospital_unit.dart';

class SearchResult {
  const SearchResult({required this.unit, required this.score});
  final HospitalUnit unit;
  final int score;
}

import 'package:flutter_test/flutter_test.dart';
import 'package:sdh_navigasyon/features/destination/data/hospital_unit_repository_impl.dart';
import 'package:sdh_navigasyon/features/search/domain/services/search_service.dart';

void main() {
  test('searches repository units by name', () async {
    final service = SearchService(const HospitalUnitRepositoryImpl());
    final results = await service.search('lavabo');
    expect(results.single.unit.name, 'Tuvaletler / Lavabolar');
  });
}

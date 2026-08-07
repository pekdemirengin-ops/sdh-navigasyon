import '../models/hospital_unit.dart';

abstract interface class HospitalUnitRepository {
  Future<List<HospitalUnit>> getAll();
}

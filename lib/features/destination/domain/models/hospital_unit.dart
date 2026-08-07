class HospitalUnit {
  const HospitalUnit({
    required this.id,
    required this.name,
    required this.floor,
    required this.directions,
    required this.mapAsset,
    this.aliases = const [],
  });

  final String id;
  final String name;
  final String floor;
  final String directions;
  final String mapAsset;
  final List<String> aliases;
}

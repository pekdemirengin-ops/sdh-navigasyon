import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/destination/presentation/destination_screen.dart';
import '../../features/favorites/presentation/favorites_screen.dart';
import '../../features/home/presentation/home_screen.dart';
import '../../features/map/presentation/map_screen.dart';
import '../../features/recent/presentation/recent_screen.dart';
import '../../features/search/domain/models/search_result.dart';
import '../../features/search/presentation/search_screen.dart';
import '../../features/settings/presentation/settings_screen.dart';

abstract final class AppRoutes {
  static const home = '/';
  static const search = '/search';
  static const destination = '/destination';
  static const map = '/map';
  static const favorites = '/favorites';
  static const recent = '/recent';
  static const settings = '/settings';
}

final appRouterProvider = Provider<GoRouter>((ref) => GoRouter(
      routes: [
        GoRoute(path: AppRoutes.home, builder: (_, __) => const HomeScreen()),
        GoRoute(path: AppRoutes.search, builder: (_, __) => const SearchScreen()),
        GoRoute(
          path: AppRoutes.destination,
          builder: (_, state) => DestinationScreen(result: state.extra! as SearchResult),
        ),
        GoRoute(path: AppRoutes.map, builder: (_, __) => const MapScreen()),
        GoRoute(path: AppRoutes.favorites, builder: (_, __) => const FavoritesScreen()),
        GoRoute(path: AppRoutes.recent, builder: (_, __) => const RecentScreen()),
        GoRoute(path: AppRoutes.settings, builder: (_, __) => const SettingsScreen()),
      ],
    ));

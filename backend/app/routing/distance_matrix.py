import math
import json
import logging
import urllib.request
import urllib.error
import numpy as np
from typing import List, Tuple, Dict
from app.schemas import DepotBase, CollectionPointBase
from app.config import settings

logger = logging.getLogger("ecoroute.osrm")

# In-memory matrix cache to ensure sub-millisecond repeated lookups
_MATRIX_CACHE: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
_GEOMETRY_CACHE: Dict[str, List[List[float]]] = {}

EARTH_RADIUS_KM = 6371.0

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Fallback straight-line geodesic distance in km."""
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c

def compute_matrices(
    depot: DepotBase,
    points: List[CollectionPointBase],
    speed_kmh: float = 35.0
) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
    """
    Computes real road-network distance matrix (km) and travel duration matrix (mins)
    using the OpenStreetMap OSRM Table service.
    Index 0 is always the central municipal depot.
    """
    all_locations = [{
        "id": 0,
        "name": depot.name,
        "latitude": depot.latitude,
        "longitude": depot.longitude,
        "waste_demand_kg": 0.0,
        "service_time_min": 0.0
    }]
    for p in points:
        all_locations.append({
            "id": p.id,
            "name": p.name,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "waste_demand_kg": p.waste_demand_kg,
            "service_time_min": p.service_time_min
        })

    n = len(all_locations)
    cache_key = f"{depot.latitude:.4f},{depot.longitude:.4f}_" + "_".join(
        f"{p['id']}:{p['latitude']:.4f},{p['longitude']:.4f}" for p in all_locations[1:]
    )

    if cache_key in _MATRIX_CACHE:
        dist_mat, time_mat = _MATRIX_CACHE[cache_key]
        return dist_mat.copy(), time_mat.copy(), all_locations

    # 1. Attempt OSRM Table API query
    try:
        coords_str = ";".join(f"{loc['longitude']:.6f},{loc['latitude']:.6f}" for loc in all_locations)
        url = f"{settings.OSRM_ROUTER_URL}/table/v1/driving/{coords_str}?annotations=distance,duration"

        req = urllib.request.Request(url, headers={"User-Agent": "EcoRoute-MSWM-RouteOptimizer"})
        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                if data.get("code") == "Ok" and "distances" in data:
                    raw_dist = np.array(data["distances"], dtype=float)  # in meters
                    raw_dur = np.array(data["durations"], dtype=float)   # in seconds

                    distance_matrix = raw_dist / 1000.0  # convert to km
                    time_matrix = raw_dur / 60.0         # convert to minutes

                    _MATRIX_CACHE[cache_key] = (distance_matrix.copy(), time_matrix.copy())
                    logger.info(f"OSRM Table Matrix successfully fetched for {n} locations.")
                    return distance_matrix, time_matrix, all_locations

    except Exception as e:
        logger.warning(f"OSRM service query failed ({e}). Falling back to road-adjusted geodesic calculation.")

    # 2. Fallback if OSRM is unreachable
    distance_matrix = np.zeros((n, n), dtype=float)
    time_matrix = np.zeros((n, n), dtype=float)

    for i in range(n):
        for j in range(n):
            if i != j:
                dist = _haversine_km(
                    all_locations[i]["latitude"], all_locations[i]["longitude"],
                    all_locations[j]["latitude"], all_locations[j]["longitude"]
                ) * 1.28  # Urban circuity factor
                distance_matrix[i][j] = dist
                time_matrix[i][j] = (dist / max(10.0, speed_kmh)) * 60.0

    _MATRIX_CACHE[cache_key] = (distance_matrix.copy(), time_matrix.copy())
    return distance_matrix, time_matrix, all_locations

def fetch_road_route_geometry(waypoints: List[List[float]]) -> List[List[float]]:
    """
    Fetches the actual street-level polyline geometry for a vehicle route
    using the OpenStreetMap OSRM Route service.
    
    Input: waypoints as [[lat, lon], [lat, lon], ...]
    Output: list of detailed [[lat, lon], ...] tracing real streets and turns.
    """
    if len(waypoints) < 2:
        return waypoints

    # Check cache
    cache_key = ";".join(f"{p[0]:.5f},{p[1]:.5f}" for p in waypoints)
    if cache_key in _GEOMETRY_CACHE:
        return _GEOMETRY_CACHE[cache_key]

    try:
        # OSRM expects {longitude},{latitude}
        coords_str = ";".join(f"{p[1]:.6f},{p[0]:.6f}" for p in waypoints)
        url = f"{settings.OSRM_ROUTER_URL}/route/v1/driving/{coords_str}?overview=full&geometries=geojson"

        req = urllib.request.Request(url, headers={"User-Agent": "EcoRoute-MSWM-RouteOptimizer"})
        with urllib.request.urlopen(req, timeout=6) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                if data.get("code") == "Ok" and data.get("routes"):
                    geojson_coords = data["routes"][0]["geometry"]["coordinates"]
                    # Convert GeoJSON [lon, lat] -> Leaflet [lat, lon]
                    street_path = [[c[1], c[0]] for c in geojson_coords]
                    _GEOMETRY_CACHE[cache_key] = street_path
                    return street_path

    except Exception as err:
        logger.warning(f"OSRM route geometry query failed ({err}). Using direct waypoints.")

    # Fallback to direct waypoints
    return waypoints

import math
import numpy as np
from typing import List, Tuple, Dict
from app.schemas import DepotBase, CollectionPointBase

EARTH_RADIUS_KM = 6371.0
ROAD_CIRCUITY_FACTOR = 1.28  # Urban road network multiplier over geodesic straight-line

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in km."""
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c

def road_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Estimate urban road distance considering street layout."""
    straight = haversine_distance(lat1, lon1, lat2, lon2)
    if straight < 0.001:
        return 0.0
    return straight * ROAD_CIRCUITY_FACTOR

def compute_matrices(
    depot: DepotBase,
    points: List[CollectionPointBase],
    speed_kmh: float = 35.0,
    traffic_factor: float = 1.0
) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
    """
    Returns:
    - distance_matrix (in km, shape (N, N))
    - time_matrix (in minutes, shape (N, N))
    - all_locations (list of dicts with id, name, lat, lng, demand, service_time)
      Index 0 is always the depot.
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
    distance_matrix = np.zeros((n, n), dtype=float)
    time_matrix = np.zeros((n, n), dtype=float)

    effective_speed = max(10.0, speed_kmh / traffic_factor)

    for i in range(n):
        for j in range(n):
            if i == j:
                distance_matrix[i][j] = 0.0
                time_matrix[i][j] = 0.0
            else:
                dist = road_distance(
                    all_locations[i]["latitude"],
                    all_locations[i]["longitude"],
                    all_locations[j]["latitude"],
                    all_locations[j]["longitude"]
                )
                distance_matrix[i][j] = dist
                # Time in minutes = (distance / speed) * 60 + destination service time
                travel_time_min = (dist / effective_speed) * 60.0
                time_matrix[i][j] = travel_time_min

    return distance_matrix, time_matrix, all_locations

def generate_interpolated_path(coords: List[List[float]], curvature: float = 0.0003) -> List[List[float]]:
    """
    Generates smooth route waypoints for visualization on Leaflet map.
    """
    if len(coords) < 2:
        return coords

    detailed_path = []
    for k in range(len(coords) - 1):
        p1 = coords[k]
        p2 = coords[k + 1]
        detailed_path.append(p1)

        # Insert 3 intermediate sub-waypoints with slight road curvature
        steps = 4
        dlat = (p2[0] - p1[0]) / steps
        dlon = (p2[1] - p1[1]) / steps
        
        # Perpendicular normal for realistic road offset
        nx = -(p2[1] - p1[1])
        ny = (p2[0] - p1[0])
        norm = math.sqrt(nx * nx + ny * ny)
        if norm > 1e-7:
            nx /= norm
            ny /= norm
        else:
            nx, ny = 0, 0

        for step in range(1, steps):
            curve_offset = math.sin(step * math.pi / steps) * curvature
            mid_lat = p1[0] + dlat * step + ny * curve_offset
            mid_lon = p1[1] + dlon * step + nx * curve_offset
            detailed_path.append([mid_lat, mid_lon])

    detailed_path.append(coords[-1])
    return detailed_path

import time
from typing import List, Dict
import numpy as np
from app.schemas import VehicleBase, OptimizationResult, VehicleRoute, RouteStep
from app.routing.distance_matrix import fetch_road_route_geometry

def solve_nearest_neighbor(
    all_locations: List[Dict],
    distance_matrix: np.ndarray,
    time_matrix: np.ndarray,
    vehicles: List[VehicleBase]
) -> OptimizationResult:
    start_time = time.time()
    n_points = len(all_locations)
    unvisited = set(range(1, n_points))
    routes_output: List[VehicleRoute] = []

    total_system_distance = 0.0
    total_system_time = 0.0
    total_system_waste = 0.0
    total_system_capacity = sum(v.capacity_kg for v in vehicles)
    capacity_violations = 0

    for vehicle in vehicles:
        if not unvisited:
            break

        current_node = 0  # Depot
        current_load = 0.0
        route_dist = 0.0
        route_time = 0.0
        route_steps: List[RouteStep] = []
        path_coords: List[List[float]] = []

        # Start step at Depot
        depot = all_locations[0]
        route_steps.append(RouteStep(
            point_id=0,
            name=depot["name"],
            latitude=depot["latitude"],
            longitude=depot["longitude"],
            waste_demand_kg=0.0,
            accumulated_waste_kg=0.0,
            distance_from_prev_km=0.0,
            travel_time_from_prev_min=0.0,
            step_type="depot_start"
        ))
        path_coords.append([depot["latitude"], depot["longitude"]])

        while unvisited:
            best_candidate = None
            best_distance = float("inf")

            for candidate in unvisited:
                demand = all_locations[candidate]["waste_demand_kg"]
                if current_load + demand <= vehicle.capacity_kg:
                    d = distance_matrix[current_node][candidate]
                    if d < best_distance:
                        best_distance = d
                        best_candidate = candidate

            if best_candidate is None:
                break

            unvisited.remove(best_candidate)
            d = distance_matrix[current_node][best_candidate]
            t = time_matrix[current_node][best_candidate] + all_locations[best_candidate]["service_time_min"]
            demand = all_locations[best_candidate]["waste_demand_kg"]

            current_load += demand
            route_dist += d
            route_time += t

            cand_loc = all_locations[best_candidate]
            route_steps.append(RouteStep(
                point_id=cand_loc["id"],
                name=cand_loc["name"],
                latitude=cand_loc["latitude"],
                longitude=cand_loc["longitude"],
                waste_demand_kg=demand,
                accumulated_waste_kg=round(current_load, 1),
                distance_from_prev_km=round(d, 2),
                travel_time_from_prev_min=round(t, 1),
                step_type="collection"
            ))
            path_coords.append([cand_loc["latitude"], cand_loc["longitude"]])
            current_node = best_candidate

        # Return to Depot
        return_dist = distance_matrix[current_node][0]
        return_time = time_matrix[current_node][0]
        route_dist += return_dist
        route_time += return_time

        route_steps.append(RouteStep(
            point_id=0,
            name=depot["name"],
            latitude=depot["latitude"],
            longitude=depot["longitude"],
            waste_demand_kg=0.0,
            accumulated_waste_kg=round(current_load, 1),
            distance_from_prev_km=round(return_dist, 2),
            travel_time_from_prev_min=round(return_time, 1),
            step_type="depot_end"
        ))
        path_coords.append([depot["latitude"], depot["longitude"]])

        if len(route_steps) > 2:
            real_street_path = fetch_road_route_geometry(path_coords)
            utilization = round((current_load / vehicle.capacity_kg) * 100.0, 1)

            routes_output.append(VehicleRoute(
                vehicle_id=vehicle.id,
                vehicle_name=vehicle.name,
                capacity_kg=vehicle.capacity_kg,
                total_waste_collected_kg=round(current_load, 1),
                capacity_utilization_pct=min(100.0, utilization),
                total_distance_km=round(route_dist, 2),
                total_time_min=round(route_time, 1),
                steps=route_steps,
                path_coordinates=real_street_path
            ))

            total_system_distance += route_dist
            total_system_time += route_time
            total_system_waste += current_load

    if unvisited:
        capacity_violations = len(unvisited)

    exec_time_ms = round((time.time() - start_time) * 1000.0, 2)
    vehicles_used = len(routes_output)

    co2_kg = round(total_system_distance * 0.85, 2)
    fuel_liters = round(total_system_distance * 0.32, 2)

    return OptimizationResult(
        algorithm="nearest_neighbor",
        algorithm_name="Nearest Neighbor (Baseline)",
        execution_time_ms=exec_time_ms,
        total_distance_km=round(total_system_distance, 2),
        total_time_min=round(total_system_time, 1),
        vehicles_used=vehicles_used,
        total_capacity_kg=round(total_system_capacity, 1),
        total_waste_kg=round(total_system_waste, 1),
        capacity_violations=capacity_violations,
        estimated_co2_kg=co2_kg,
        estimated_fuel_liters=fuel_liters,
        objective_cost=round(total_system_distance, 2),
        routes=routes_output
    )

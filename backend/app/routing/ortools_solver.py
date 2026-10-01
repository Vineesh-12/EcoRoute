import time
from typing import List, Dict
import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from app.schemas import VehicleBase, OptimizationResult, VehicleRoute, RouteStep
from app.routing.distance_matrix import generate_interpolated_path

def solve_ortools_cvrp(
    all_locations: List[Dict],
    distance_matrix: np.ndarray,
    time_matrix: np.ndarray,
    vehicles: List[VehicleBase],
    time_limit_sec: int = 2
) -> OptimizationResult:
    """
    Solves Capacitated Vehicle Routing Problem (CVRP) using Google OR-Tools.
    Acts as the optimization benchmark solver.
    """
    start_time = time.time()
    num_nodes = len(all_locations)
    num_vehicles = len(vehicles)

    if num_nodes <= 1:
        return OptimizationResult(
            algorithm="ortools",
            algorithm_name="Google OR-Tools (Benchmark Solver)",
            execution_time_ms=0.0,
            total_distance_km=0.0,
            total_time_min=0.0,
            vehicles_used=0,
            total_capacity_kg=sum(v.capacity_kg for v in vehicles),
            total_waste_kg=0.0,
            capacity_violations=0,
            estimated_co2_kg=0.0,
            estimated_fuel_liters=0.0,
            objective_cost=0.0,
            routes=[]
        )

    # 1. Create Routing Index Manager (depot is index 0)
    manager = pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    # 2. Register Transit Callback (Distance in meters for integer precision)
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # Convert km to meters
        return int(round(distance_matrix[from_node][to_node] * 1000))

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 3. Add Capacity Dimension
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return int(round(all_locations[from_node]["waste_demand_kg"]))

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    
    capacities = [int(round(v.capacity_kg)) for v in vehicles]
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        capacities,  # vehicle maximum capacities
        True,  # start cumul to zero
        "Capacity"
    )

    # Allow dropping visits only with very high penalty if capacity is physically insufficient
    penalty = 1000000
    for node in range(1, num_nodes):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    # 4. Search Parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = time_limit_sec

    # 5. Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    exec_time_ms = round((time.time() - start_time) * 1000.0, 2)

    if not solution:
        # Fallback if no solution found
        return OptimizationResult(
            algorithm="ortools",
            algorithm_name="Google OR-Tools (Benchmark Solver)",
            execution_time_ms=exec_time_ms,
            total_distance_km=0.0,
            total_time_min=0.0,
            vehicles_used=0,
            total_capacity_kg=sum(v.capacity_kg for v in vehicles),
            total_waste_kg=0.0,
            capacity_violations=num_nodes - 1,
            estimated_co2_kg=0.0,
            estimated_fuel_liters=0.0,
            objective_cost=0.0,
            routes=[]
        )

    # 6. Extract Routes
    depot = all_locations[0]
    routes_output: List[VehicleRoute] = []
    total_system_dist = 0.0
    total_system_time = 0.0
    total_system_waste = 0.0
    unassigned_count = 0

    for node in range(1, num_nodes):
        if routing.IsStart(manager.NodeToIndex(node)) or routing.IsEnd(manager.NodeToIndex(node)):
            continue
        if solution.Value(routing.NextVar(manager.NodeToIndex(node))) == manager.NodeToIndex(node):
            unassigned_count += 1

    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route_nodes = []
        route_dist_meters = 0
        route_time = 0.0
        route_load = 0.0
        route_steps: List[RouteStep] = []
        path_coords: List[List[float]] = []

        # Start at Depot
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

        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            next_node = manager.IndexToNode(index)

            if next_node != 0:
                step_dist = distance_matrix[node_index][next_node]
                step_time = time_matrix[node_index][next_node] + all_locations[next_node]["service_time_min"]
                demand = all_locations[next_node]["waste_demand_kg"]
                
                route_dist_meters += int(round(step_dist * 1000))
                route_time += step_time
                route_load += demand

                cand_loc = all_locations[next_node]
                route_steps.append(RouteStep(
                    point_id=cand_loc["id"],
                    name=cand_loc["name"],
                    latitude=cand_loc["latitude"],
                    longitude=cand_loc["longitude"],
                    waste_demand_kg=demand,
                    accumulated_waste_kg=round(route_load, 1),
                    distance_from_prev_km=round(step_dist, 2),
                    travel_time_from_prev_min=round(step_time, 1),
                    step_type="collection"
                ))
                path_coords.append([cand_loc["latitude"], cand_loc["longitude"]])
            else:
                # Return to depot
                step_dist = distance_matrix[node_index][0]
                step_time = time_matrix[node_index][0]
                route_dist_meters += int(round(step_dist * 1000))
                route_time += step_time

                route_steps.append(RouteStep(
                    point_id=0,
                    name=depot["name"],
                    latitude=depot["latitude"],
                    longitude=depot["longitude"],
                    waste_demand_kg=0.0,
                    accumulated_waste_kg=round(route_load, 1),
                    distance_from_prev_km=round(step_dist, 2),
                    travel_time_from_prev_min=round(step_time, 1),
                    step_type="depot_end"
                ))
                path_coords.append([depot["latitude"], depot["longitude"]])

        # If vehicle served any collection point
        if len(route_steps) > 2:
            vehicle = vehicles[vehicle_id]
            route_dist_km = round(route_dist_meters / 1000.0, 2)
            interpolated = generate_interpolated_path(path_coords)
            utilization = round((route_load / vehicle.capacity_kg) * 100.0, 1)

            routes_output.append(VehicleRoute(
                vehicle_id=vehicle.id,
                vehicle_name=vehicle.name,
                capacity_kg=vehicle.capacity_kg,
                total_waste_collected_kg=round(route_load, 1),
                capacity_utilization_pct=min(100.0, utilization),
                total_distance_km=route_dist_km,
                total_time_min=round(route_time, 1),
                steps=route_steps,
                path_coordinates=interpolated
            ))

            total_system_dist += route_dist_km
            total_system_time += route_time
            total_system_waste += route_load

    total_capacity = sum(v.capacity_kg for v in vehicles)
    co2_kg = round(total_system_dist * 0.85, 2)
    fuel_liters = round(total_system_dist * 0.32, 2)

    return OptimizationResult(
        algorithm="ortools",
        algorithm_name="Google OR-Tools (Benchmark Solver)",
        execution_time_ms=exec_time_ms,
        total_distance_km=round(total_system_dist, 2),
        total_time_min=round(total_system_time, 1),
        vehicles_used=len(routes_output),
        total_capacity_kg=round(total_capacity, 1),
        total_waste_kg=round(total_system_waste, 1),
        capacity_violations=unassigned_count,
        estimated_co2_kg=co2_kg,
        estimated_fuel_liters=fuel_liters,
        objective_cost=round(total_system_dist, 2),
        routes=routes_output
    )

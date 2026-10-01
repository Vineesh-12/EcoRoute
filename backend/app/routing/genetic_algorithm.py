import time
import random
from typing import List, Dict, Tuple
import numpy as np
from app.schemas import VehicleBase, OptimizationResult, VehicleRoute, RouteStep
from app.routing.distance_matrix import fetch_road_route_geometry

def decode_chromosome(
    chromosome: List[int],
    all_locations: List[Dict],
    distance_matrix: np.ndarray,
    time_matrix: np.ndarray,
    vehicles: List[VehicleBase]
) -> Tuple[List[List[int]], float, float, int]:
    """
    Decodes a permutation chromosome into vehicle routes satisfying vehicle capacities.
    Returns:
    - routes: list of lists of point indices (excluding depot)
    - total_distance: float
    - total_time: float
    - unassigned_count: int
    """
    vehicle_routes: List[List[int]] = [[] for _ in vehicles]
    vehicle_loads = [0.0 for _ in vehicles]
    current_vehicle_idx = 0

    for point_idx in chromosome:
        demand = all_locations[point_idx]["waste_demand_kg"]
        assigned = False

        if current_vehicle_idx < len(vehicles):
            if vehicle_loads[current_vehicle_idx] + demand <= vehicles[current_vehicle_idx].capacity_kg:
                vehicle_routes[current_vehicle_idx].append(point_idx)
                vehicle_loads[current_vehicle_idx] += demand
                assigned = True
            else:
                current_vehicle_idx += 1
                if current_vehicle_idx < len(vehicles):
                    vehicle_routes[current_vehicle_idx].append(point_idx)
                    vehicle_loads[current_vehicle_idx] += demand
                    assigned = True

        if not assigned:
            for v_idx in range(len(vehicles)):
                if vehicle_loads[v_idx] + demand <= vehicles[v_idx].capacity_kg:
                    vehicle_routes[v_idx].append(point_idx)
                    vehicle_loads[v_idx] += demand
                    assigned = True
                    break

    total_dist = 0.0
    total_time = 0.0

    assigned_set = set()
    for r in vehicle_routes:
        assigned_set.update(r)

    unassigned = len(chromosome) - len(assigned_set)

    for route in vehicle_routes:
        if not route:
            continue
        prev = 0
        for node in route:
            total_dist += distance_matrix[prev][node]
            total_time += time_matrix[prev][node] + all_locations[node]["service_time_min"]
            prev = node
        total_dist += distance_matrix[prev][0]
        total_time += time_matrix[prev][0]

    return vehicle_routes, total_dist, total_time, unassigned

def order_crossover(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
    """Order Crossover (OX) for permutation chromosomes."""
    size = len(parent1)
    if size < 2:
        return parent1[:], parent2[:]

    cx1, cx2 = sorted(random.sample(range(size), 2))

    def make_child(p1, p2):
        child = [-1] * size
        child[cx1:cx2 + 1] = p1[cx1:cx2 + 1]
        p1_set = set(child[cx1:cx2 + 1])
        fill_vals = [item for item in p2 if item not in p1_set]
        
        idx = 0
        for i in range(size):
            if child[i] == -1:
                child[i] = fill_vals[idx]
                idx += 1
        return child

    return make_child(parent1, parent2), make_child(parent2, parent1)

def mutate(chromosome: List[int], mutation_rate: float = 0.25) -> List[int]:
    """Inversion (2-opt style) and Swap mutation."""
    chrom = chromosome[:]
    if random.random() < mutation_rate and len(chrom) > 2:
        i, j = sorted(random.sample(range(len(chrom)), 2))
        chrom[i:j + 1] = reversed(chrom[i:j + 1])

    if random.random() < mutation_rate and len(chrom) > 1:
        i, j = random.sample(range(len(chrom)), 2)
        chrom[i], chrom[j] = chrom[j], chrom[i]

    return chrom

def solve_genetic_algorithm(
    all_locations: List[Dict],
    distance_matrix: np.ndarray,
    time_matrix: np.ndarray,
    vehicles: List[VehicleBase],
    population_size: int = 60,
    generations: int = 100
) -> OptimizationResult:
    start_time = time.time()
    n_points = len(all_locations)
    customer_indices = list(range(1, n_points))

    if not customer_indices:
        return OptimizationResult(
            algorithm="genetic_algorithm",
            algorithm_name="Genetic Algorithm (Metaheuristic)",
            execution_time_ms=0.0,
            total_distance_km=0.0,
            total_time_min=0.0,
            vehicles_used=0,
            total_capacity_kg=0.0,
            total_waste_kg=0.0,
            capacity_violations=0,
            estimated_co2_kg=0.0,
            estimated_fuel_liters=0.0,
            objective_cost=0.0,
            routes=[]
        )

    # Initialize Population
    population: List[List[int]] = []
    # Seed with nearest-neighbor greedy tour
    curr = 0
    remaining = set(customer_indices)
    greedy_order = []
    while remaining:
        nxt = min(remaining, key=lambda c: distance_matrix[curr][c])
        greedy_order.append(nxt)
        remaining.remove(nxt)
        curr = nxt
    population.append(greedy_order)

    for _ in range(population_size - 1):
        ind = customer_indices[:]
        random.shuffle(ind)
        population.append(ind)

    def evaluate_fitness(chrom: List[int]) -> Tuple[float, float, float, int, List[List[int]]]:
        routes, dist, t_time, unassigned = decode_chromosome(
            chrom, all_locations, distance_matrix, time_matrix, vehicles
        )
        # Cost is strictly total road distance with heavy penalty for unassigned bins
        cost = dist + (unassigned * 1000.0)
        return cost, dist, t_time, unassigned, routes

    best_individual = None
    best_cost = float("inf")
    best_dist = 0.0
    best_time = 0.0
    best_unassigned = 0
    best_routes = []

    elite_count = max(2, int(population_size * 0.08))

    for gen in range(generations):
        evaluated = []
        for ind in population:
            cost, dist, t_time, unassigned, routes = evaluate_fitness(ind)
            evaluated.append((cost, dist, t_time, unassigned, routes, ind))
            if cost < best_cost:
                best_cost = cost
                best_dist = dist
                best_time = t_time
                best_unassigned = unassigned
                best_routes = routes
                best_individual = ind[:]

        evaluated.sort(key=lambda x: x[0])
        new_population = [evaluated[i][5][:] for i in range(elite_count)]

        while len(new_population) < population_size:
            t1 = random.sample(evaluated, 3)
            p1 = min(t1, key=lambda x: x[0])[5]

            t2 = random.sample(evaluated, 3)
            p2 = min(t2, key=lambda x: x[0])[5]

            c1, c2 = order_crossover(p1, p2)
            new_population.append(mutate(c1))
            if len(new_population) < population_size:
                new_population.append(mutate(c2))

        population = new_population

    depot = all_locations[0]
    routes_output: List[VehicleRoute] = []
    total_waste = 0.0

    for v_idx, route in enumerate(best_routes):
        if not route:
            continue
        vehicle = vehicles[v_idx]
        current_load = sum(all_locations[node]["waste_demand_kg"] for node in route)
        total_waste += current_load

        route_steps: List[RouteStep] = []
        path_coords: List[List[float]] = []

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

        prev = 0
        cum_waste = 0.0
        route_dist = 0.0
        route_time = 0.0

        for node in route:
            d = distance_matrix[prev][node]
            t = time_matrix[prev][node] + all_locations[node]["service_time_min"]
            demand = all_locations[node]["waste_demand_kg"]
            cum_waste += demand
            route_dist += d
            route_time += t

            cand_loc = all_locations[node]
            route_steps.append(RouteStep(
                point_id=cand_loc["id"],
                name=cand_loc["name"],
                latitude=cand_loc["latitude"],
                longitude=cand_loc["longitude"],
                waste_demand_kg=demand,
                accumulated_waste_kg=round(cum_waste, 1),
                distance_from_prev_km=round(d, 2),
                travel_time_from_prev_min=round(t, 1),
                step_type="collection"
            ))
            path_coords.append([cand_loc["latitude"], cand_loc["longitude"]])
            prev = node

        return_dist = distance_matrix[prev][0]
        return_time = time_matrix[prev][0]
        route_dist += return_dist
        route_time += return_time

        route_steps.append(RouteStep(
            point_id=0,
            name=depot["name"],
            latitude=depot["latitude"],
            longitude=depot["longitude"],
            waste_demand_kg=0.0,
            accumulated_waste_kg=round(cum_waste, 1),
            distance_from_prev_km=round(return_dist, 2),
            travel_time_from_prev_min=round(return_time, 1),
            step_type="depot_end"
        ))
        path_coords.append([depot["latitude"], depot["longitude"]])

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

    exec_time_ms = round((time.time() - start_time) * 1000.0, 2)
    total_capacity = sum(v.capacity_kg for v in vehicles)
    co2_kg = round(best_dist * 0.85, 2)
    fuel_liters = round(best_dist * 0.32, 2)

    return OptimizationResult(
        algorithm="genetic_algorithm",
        algorithm_name="Genetic Algorithm (Metaheuristic)",
        execution_time_ms=exec_time_ms,
        total_distance_km=round(best_dist, 2),
        total_time_min=round(best_time, 1),
        vehicles_used=len(routes_output),
        total_capacity_kg=round(total_capacity, 1),
        total_waste_kg=round(total_waste, 1),
        capacity_violations=best_unassigned,
        estimated_co2_kg=co2_kg,
        estimated_fuel_liters=fuel_liters,
        objective_cost=round(best_dist, 2),
        routes=routes_output
    )

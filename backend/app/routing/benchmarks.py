import time
from typing import Dict, List
import numpy as np

from app.schemas import (
    DepotBase,
    CollectionPointBase,
    VehicleBase,
    Weights,
    OptimizationResult,
    SavingsMetric,
    OptimizationComparison
)
from app.routing.distance_matrix import compute_matrices
from app.routing.nearest_neighbor import solve_nearest_neighbor
from app.routing.genetic_algorithm import solve_genetic_algorithm
from app.routing.ortools_solver import solve_ortools_cvrp

def run_cvrp_comparison(
    depot: DepotBase,
    points: List[CollectionPointBase],
    vehicles: List[VehicleBase],
    scenario_name: str = "Municipal Route Optimization"
) -> OptimizationComparison:
    """
    Executes all three algorithms on the exact same CVRP instance:
    1. Baseline Heuristic: Nearest Neighbor
    2. Metaheuristic: Genetic Algorithm
    3. Optimization Benchmark Solver: Google OR-Tools
    
    Computes Before-vs-After savings relative to the Nearest Neighbor baseline.
    """
    # 1. Compute distance & travel time matrices
    dist_matrix, time_matrix, all_locations = compute_matrices(
        depot=depot,
        points=points,
        speed_kmh=35.0,
        traffic_factor=1.0
    )

    weights = Weights(distance=1.0, time=0.0, vehicles=0.0)

    # 2. Run Nearest Neighbor (Baseline)
    nn_result = solve_nearest_neighbor(
        all_locations=all_locations,
        distance_matrix=dist_matrix,
        time_matrix=time_matrix,
        vehicles=vehicles,
        weights=weights
    )

    # 3. Run Genetic Algorithm (Metaheuristic)
    ga_result = solve_genetic_algorithm(
        all_locations=all_locations,
        distance_matrix=dist_matrix,
        time_matrix=time_matrix,
        vehicles=vehicles,
        weights=weights,
        population_size=60,
        generations=100
    )

    # 4. Run Google OR-Tools (Optimization Benchmark Solver)
    ortools_result = solve_ortools_cvrp(
        all_locations=all_locations,
        distance_matrix=dist_matrix,
        time_matrix=time_matrix,
        vehicles=vehicles,
        time_limit_sec=2
    )

    results_map: Dict[str, OptimizationResult] = {
        "nearest_neighbor": nn_result,
        "genetic_algorithm": ga_result,
        "ortools": ortools_result
    }

    # 5. Compute Before-vs-After Savings against Nearest Neighbor Baseline
    base_dist = max(0.01, nn_result.total_distance_km)
    base_time = max(0.01, nn_result.total_time_min)

    savings_map: Dict[str, SavingsMetric] = {}

    for algo_key, res in results_map.items():
        dist_saved_km = round(base_dist - res.total_distance_km, 2)
        dist_saved_pct = round((dist_saved_km / base_dist) * 100.0, 1)
        
        time_saved_min = round(base_time - res.total_time_min, 1)
        time_saved_pct = round((time_saved_min / base_time) * 100.0, 1)

        fuel_saved_l = round(max(0.0, dist_saved_km * 0.32), 2)
        co2_saved_kg = round(max(0.0, dist_saved_km * 0.85), 2)

        savings_map[algo_key] = SavingsMetric(
            distance_saved_km=dist_saved_km,
            distance_saved_pct=dist_saved_pct,
            time_saved_min=time_saved_min,
            time_saved_pct=time_saved_pct,
            fuel_saved_liters=fuel_saved_l,
            co2_saved_kg=co2_saved_kg
        )

    # Best algorithm is whichever has lowest total distance without capacity violations
    valid_results = {
        k: v for k, v in results_map.items()
        if v.capacity_violations == 0 and v.total_distance_km > 0
    }
    if valid_results:
        best_algo = min(valid_results.keys(), key=lambda k: valid_results[k].total_distance_km)
    else:
        best_algo = min(results_map.keys(), key=lambda k: results_map[k].total_distance_km)

    return OptimizationComparison(
        baseline_algorithm="nearest_neighbor",
        best_algorithm=best_algo,
        comparison_summary=results_map,
        savings_vs_baseline=savings_map,
        scenario_name=scenario_name
    )

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.schemas import (
    OptimizationRequest,
    OptimizationResult,
    OptimizationComparison
)
from app.routing.distance_matrix import compute_matrices
from app.routing.nearest_neighbor import solve_nearest_neighbor
from app.routing.genetic_algorithm import solve_genetic_algorithm
from app.routing.ortools_solver import solve_ortools_cvrp
from app.routing.benchmarks import run_cvrp_comparison
from app.scenarios import SCENARIOS

router = APIRouter()

@router.get("/health")
def get_health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "EcoRoute Optimization Engine",
        "routing_engine": "OpenStreetMap / OSRM Real Road Network",
        "supported_algorithms": [
            {"id": "nearest_neighbor", "name": "Nearest Neighbor (Baseline Heuristic)"},
            {"id": "genetic_algorithm", "name": "Genetic Algorithm (Metaheuristic)"},
            {"id": "ortools", "name": "Google OR-Tools (Benchmark Solver)"}
        ]
    }

@router.get("/scenarios")
def get_scenarios():
    """List all pre-configured municipal scenarios."""
    results = []
    for sc_id, sc_fn in SCENARIOS.items():
        data = sc_fn()
        results.append({
            "id": data["id"],
            "name": data["name"],
            "description": data["description"],
            "num_points": len(data["collection_points"]),
            "num_vehicles": len(data["vehicles"]),
            "total_capacity_kg": sum(v.capacity_kg for v in data["vehicles"]),
            "total_demand_kg": sum(p.waste_demand_kg for p in data["collection_points"])
        })
    return results

@router.get("/scenarios/{scenario_id}")
def get_scenario_detail(scenario_id: str):
    """Retrieve full data for a scenario."""
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return SCENARIOS[scenario_id]()

@router.post("/optimize")
def optimize_routes(request: OptimizationRequest):
    """
    Run CVRP optimization on provided depot, collection points, and vehicles.
    If algorithm == 'all', returns full head-to-head comparison against baseline.
    """
    if not request.collection_points:
        raise HTTPException(status_code=400, detail="At least one collection point is required.")
    if not request.vehicles:
        raise HTTPException(status_code=400, detail="At least one vehicle is required.")

    if request.algorithm.lower() in ("all", "compare"):
        return run_cvrp_comparison(
            depot=request.depot,
            points=request.collection_points,
            vehicles=request.vehicles,
            scenario_name="Custom Routing Plan"
        )

    dist_matrix, time_matrix, all_locations = compute_matrices(
        depot=request.depot,
        points=request.collection_points,
        speed_kmh=35.0
    )

    algo = request.algorithm.lower()

    if algo == "nearest_neighbor":
        result = solve_nearest_neighbor(all_locations, dist_matrix, time_matrix, request.vehicles)
    elif algo in ("genetic_algorithm", "ga"):
        result = solve_genetic_algorithm(all_locations, dist_matrix, time_matrix, request.vehicles)
    elif algo in ("ortools", "or_tools"):
        result = solve_ortools_cvrp(all_locations, dist_matrix, time_matrix, request.vehicles)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown algorithm: {request.algorithm}. Use 'nearest_neighbor', 'genetic_algorithm', 'ortools', or 'all'."
        )

    return result

@router.post("/benchmark", response_model=OptimizationComparison)
def run_benchmark(request: OptimizationRequest):
    """
    Run all three algorithms (Nearest Neighbor, Genetic Algorithm, OR-Tools)
    and return Before-vs-After savings metrics.
    """
    return run_cvrp_comparison(
        depot=request.depot,
        points=request.collection_points,
        vehicles=request.vehicles,
        scenario_name="Benchmark Run"
    )

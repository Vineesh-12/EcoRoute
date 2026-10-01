from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class Location(BaseModel):
    latitude: float
    longitude: float

class DepotBase(BaseModel):
    name: str = "Central Waste Depot"
    latitude: float
    longitude: float
    address: Optional[str] = "Central Municipal Depot"

class CollectionPointBase(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    waste_demand_kg: float = Field(..., ge=1.0, description="Estimated waste in kg")
    service_time_min: float = Field(5.0, ge=0.0, description="Loading time in minutes")

class VehicleBase(BaseModel):
    id: int
    name: str
    capacity_kg: float = Field(500.0, ge=50.0, description="Vehicle payload capacity in kg")
    speed_kmh: float = 35.0

class OptimizationRequest(BaseModel):
    depot: DepotBase
    collection_points: List[CollectionPointBase]
    vehicles: List[VehicleBase]
    algorithm: str = Field("all", description="nearest_neighbor, genetic_algorithm, ortools, or all")

class RouteStep(BaseModel):
    point_id: int
    name: str
    latitude: float
    longitude: float
    waste_demand_kg: float
    accumulated_waste_kg: float
    distance_from_prev_km: float
    travel_time_from_prev_min: float
    step_type: str = "collection"  # 'depot_start', 'collection', 'depot_end'

class VehicleRoute(BaseModel):
    vehicle_id: int
    vehicle_name: str
    capacity_kg: float
    total_waste_collected_kg: float
    capacity_utilization_pct: float
    total_distance_km: float
    total_time_min: float
    steps: List[RouteStep]
    path_coordinates: List[List[float]]  # Real turn-by-turn road polyline from OSRM

class OptimizationResult(BaseModel):
    algorithm: str
    algorithm_name: str
    execution_time_ms: float
    total_distance_km: float
    total_time_min: float
    vehicles_used: int
    total_capacity_kg: float
    total_waste_kg: float
    capacity_violations: int
    estimated_co2_kg: float
    estimated_fuel_liters: float
    objective_cost: float
    routes: List[VehicleRoute]

class SavingsMetric(BaseModel):
    distance_saved_km: float
    distance_saved_pct: float
    time_saved_min: float
    time_saved_pct: float
    fuel_saved_liters: float
    co2_saved_kg: float

class OptimizationComparison(BaseModel):
    baseline_algorithm: str
    best_algorithm: str
    comparison_summary: Dict[str, OptimizationResult]
    savings_vs_baseline: Dict[str, SavingsMetric]
    scenario_name: Optional[str] = "Municipal Route Optimization"

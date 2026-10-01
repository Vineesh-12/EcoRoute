from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class Location(BaseModel):
    latitude: float
    longitude: float

class DepotBase(BaseModel):
    name: str = "Central Waste Depot"
    latitude: float
    longitude: float
    address: Optional[str] = "Municipal Yard, Sector 4"

class CollectionPointBase(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    waste_demand_kg: float = Field(..., ge=1.0, description="Estimated waste in kg")
    service_time_min: float = Field(5.0, ge=0.0, description="Loading/collection time in minutes")
    priority: int = Field(1, ge=1, le=3)

class VehicleBase(BaseModel):
    id: int
    name: str
    capacity_kg: float = Field(500.0, ge=50.0, description="Vehicle payload capacity in kg")
    max_distance_km: float = 120.0
    speed_kmh: float = 35.0
    emission_factor: float = 0.85  # kg CO2/km

class Weights(BaseModel):
    distance: float = 0.6
    time: float = 0.3
    vehicles: float = 0.1

class OptimizationRequest(BaseModel):
    depot: DepotBase
    collection_points: List[CollectionPointBase]
    vehicles: List[VehicleBase]
    algorithm: str = Field("all", description="nearest_neighbor, genetic_algorithm, ant_colony, ortools, or all")
    weights: Optional[Weights] = Field(default_factory=Weights)
    traffic_factor: float = Field(1.0, ge=0.5, le=3.0, description="Multiplier for congestion delays")

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
    path_coordinates: List[List[float]]  # [[lat, lon], ...] for drawing path on map

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
    scenario_name: Optional[str] = "Scenario"

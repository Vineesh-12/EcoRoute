import json
import os
from typing import Dict, List
from app.schemas import DepotBase, CollectionPointBase, VehicleBase

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_scenario_from_json(scenario_id: str) -> Dict:
    filepath = os.path.join(DATA_DIR, f"{scenario_id}.json")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Scenario file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)

    depot = DepotBase(**raw["depot"])
    points = [CollectionPointBase(**p) for p in raw["collection_points"]]
    vehicles = [VehicleBase(**v) for v in raw["vehicles"]]

    return {
        "id": raw["id"],
        "name": raw["name"],
        "description": raw["description"],
        "depot": depot,
        "collection_points": points,
        "vehicles": vehicles
    }

def get_scenario_urban_core() -> Dict:
    return load_scenario_from_json("urban_core")

def get_scenario_residential_ward() -> Dict:
    return load_scenario_from_json("residential_ward")

def get_scenario_city_district() -> Dict:
    return load_scenario_from_json("city_district")

SCENARIOS = {
    "urban_core": get_scenario_urban_core,
    "residential_ward": get_scenario_residential_ward,
    "city_district": get_scenario_city_district
}

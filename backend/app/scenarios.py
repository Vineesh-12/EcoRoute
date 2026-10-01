from typing import List, Dict
from app.schemas import DepotBase, CollectionPointBase, VehicleBase

# Realistic municipal scenarios based on real urban coordinates (Chennai Metropolitan Area)

def get_scenario_urban_core() -> Dict:
    """Scenario 1: Urban Core (12 points, 3 trucks x 500kg)"""
    depot = DepotBase(
        name="Central Municipal Garage (Depot)",
        latitude=13.0827,
        longitude=80.2707,
        address="Poonamallee High Rd, Central Chennai"
    )
    
    points = [
        CollectionPointBase(id=1, name="Koyambedu Wholesale Market", latitude=13.0694, longitude=80.1948, waste_demand_kg=160.0, service_time_min=8.0, priority=3),
        CollectionPointBase(id=2, name="Egmore Railway Station Yard", latitude=13.0784, longitude=80.2608, waste_demand_kg=90.0, service_time_min=5.0, priority=2),
        CollectionPointBase(id=3, name="T. Nagar Commercial Complex", latitude=13.0418, longitude=80.2341, waste_demand_kg=140.0, service_time_min=7.0, priority=3),
        CollectionPointBase(id=4, name="Alwarpet Community Bins", latitude=13.0336, longitude=80.2520, waste_demand_kg=75.0, service_time_min=4.0, priority=1),
        CollectionPointBase(id=5, name="Mylapore Temple Zone", latitude=13.0339, longitude=80.2687, waste_demand_kg=110.0, service_time_min=6.0, priority=2),
        CollectionPointBase(id=6, name="Royapettah Government Hospital", latitude=13.0558, longitude=80.2612, waste_demand_kg=85.0, service_time_min=5.0, priority=3),
        CollectionPointBase(id=7, name="Triplicane Residential Ward", latitude=13.0588, longitude=80.2755, waste_demand_kg=95.0, service_time_min=5.0, priority=1),
        CollectionPointBase(id=8, name="Nungambakkam High Road", latitude=13.0604, longitude=80.2415, waste_demand_kg=120.0, service_time_min=6.0, priority=2),
        CollectionPointBase(id=9, name="Chetpet Eco-Park Enclave", latitude=13.0719, longitude=80.2423, waste_demand_kg=60.0, service_time_min=4.0, priority=1),
        CollectionPointBase(id=10, name="Kilpauk Medical College Area", latitude=13.0792, longitude=80.2435, waste_demand_kg=80.0, service_time_min=4.0, priority=2),
        CollectionPointBase(id=11, name="Anna Nagar West Depot Point", latitude=13.0850, longitude=80.2101, waste_demand_kg=130.0, service_time_min=6.0, priority=2),
        CollectionPointBase(id=12, name="Shenoy Nagar Metro Junction", latitude=13.0779, longitude=80.2268, waste_demand_kg=70.0, service_time_min=4.0, priority=1)
    ]
    
    vehicles = [
        VehicleBase(id=1, name="EcoTruck Alpha (500kg)", capacity_kg=500.0, speed_kmh=35.0),
        VehicleBase(id=2, name="EcoTruck Beta (500kg)", capacity_kg=500.0, speed_kmh=35.0),
        VehicleBase(id=3, name="EcoTruck Gamma (500kg)", capacity_kg=500.0, speed_kmh=35.0)
    ]
    
    return {
        "id": "urban_core",
        "name": "Urban Commercial Core (12 Points, 3 Trucks)",
        "description": "High-density market zones and transit hubs requiring multi-vehicle coordination.",
        "depot": depot,
        "collection_points": points,
        "vehicles": vehicles
    }

def get_scenario_residential_ward() -> Dict:
    """Scenario 2: Residential Ward (25 points, 4 trucks x 500kg)"""
    depot = DepotBase(
        name="Municipal Solid Waste Depot",
        latitude=13.0827,
        longitude=80.2707,
        address="Central Solid Waste Facility"
    )
    
    # 25 residential and market collection clusters
    raw_points = [
        ("Anna Nagar East Ward 1", 13.0864, 80.2205, 75.0),
        ("Anna Nagar East Ward 2", 13.0898, 80.2165, 65.0),
        ("Koyambedu Market Block A", 13.0694, 80.1948, 140.0),
        ("Koyambedu Market Block B", 13.0655, 80.1980, 120.0),
        ("Arumbakkam Metro Point", 13.0620, 80.2115, 80.0),
        ("Aminjikarai Bins", 13.0710, 80.2220, 70.0),
        ("Shenoy Nagar North", 13.0815, 80.2280, 55.0),
        ("Kilpauk Garden Sector", 13.0820, 80.2390, 85.0),
        ("Chetpet Railway Colony", 13.0695, 80.2450, 60.0),
        ("Nungambakkam Lake Area", 13.0625, 80.2385, 95.0),
        ("T. Nagar Ranganathan St", 13.0405, 80.2330, 150.0),
        ("T. Nagar Panagal Park", 13.0440, 80.2355, 110.0),
        ("Kodambakkam Station Area", 13.0515, 80.2240, 80.0),
        ("Vadapalani Temple Area", 13.0520, 80.2120, 105.0),
        ("Ashok Nagar 1st Avenue", 13.0360, 80.2150, 70.0),
        ("KK Nagar Sector 5", 13.0290, 80.2010, 85.0),
        ("Alwarpet TTK Road", 13.0350, 80.2510, 75.0),
        ("Mylapore Tank Square", 13.0335, 80.2700, 115.0),
        ("Mandaveli Bus Stand", 13.0255, 80.2640, 65.0),
        ("Adyar Gandhi Nagar", 13.0110, 80.2530, 90.0),
        ("Besant Nagar Beach Rd", 13.0010, 80.2690, 80.0),
        ("Royapettah Clock Tower", 13.0570, 80.2630, 70.0),
        ("Triplicane Ice House", 13.0520, 80.2790, 85.0),
        ("Chintadripet Fish Market", 13.0735, 80.2740, 125.0),
        ("Perambur Carriage Works", 13.1110, 80.2450, 95.0),
    ]
    
    points = []
    for i, (name, lat, lon, demand) in enumerate(raw_points, start=1):
        points.append(CollectionPointBase(
            id=i,
            name=name,
            latitude=lat,
            longitude=lon,
            waste_demand_kg=demand,
            service_time_min=5.0,
            priority=2 if demand > 100 else 1
        ))
        
    vehicles = [
        VehicleBase(id=1, name="EcoTruck 1 (500kg)", capacity_kg=500.0, speed_kmh=35.0),
        VehicleBase(id=2, name="EcoTruck 2 (500kg)", capacity_kg=500.0, speed_kmh=35.0),
        VehicleBase(id=3, name="EcoTruck 3 (500kg)", capacity_kg=500.0, speed_kmh=35.0),
        VehicleBase(id=4, name="EcoTruck 4 (500kg)", capacity_kg=500.0, speed_kmh=35.0),
    ]
    
    return {
        "id": "residential_ward",
        "name": "Residential & Market Ward (25 Points, 4 Trucks)",
        "description": "Suburban spread across mixed residential and commercial hubs.",
        "depot": depot,
        "collection_points": points,
        "vehicles": vehicles
    }

def get_scenario_city_district() -> Dict:
    """Scenario 3: City District (40 points, 5 trucks x 600kg)"""
    res = get_scenario_residential_ward()
    depot = res["depot"]
    points = list(res["collection_points"])
    
    extra_points = [
        ("Guindy Industrial Estate", 13.0070, 80.2120, 150.0),
        ("Saidapet Market", 13.0210, 80.2230, 130.0),
        ("West Mambalam Canal Rd", 13.0370, 80.2230, 95.0),
        ("Ekkatuthangal Metro", 13.0180, 80.2030, 85.0),
        ("Porur Junction Point", 13.0350, 80.1580, 140.0),
        ("Kattupakkam Hub", 13.0450, 80.1380, 90.0),
        ("Mogappair East Ward", 13.0880, 80.1810, 80.0),
        ("Ambattur Estate Road", 13.1040, 80.1650, 160.0),
        ("Kolathur Lake Side", 13.1220, 80.2180, 75.0),
        ("Villivakkam Railway Yard", 13.1080, 80.2050, 85.0),
        ("Ayanavaram Joint Bins", 13.0970, 80.2310, 90.0),
        ("Purasawalkam Market", 13.0900, 80.2550, 135.0),
        ("Sowcarpet Wholesale Hub", 13.0930, 80.2780, 175.0),
        ("George Town Port Gate", 13.0980, 80.2920, 110.0),
        ("Royapuram Fishery Road", 13.1110, 80.2970, 120.0),
    ]
    
    start_id = len(points) + 1
    for i, (name, lat, lon, demand) in enumerate(extra_points, start=start_id):
        points.append(CollectionPointBase(
            id=i,
            name=name,
            latitude=lat,
            longitude=lon,
            waste_demand_kg=demand,
            service_time_min=5.0,
            priority=3 if demand > 120 else 1
        ))
        
    vehicles = [
        VehicleBase(id=1, name="EcoTruck Heavy 1 (600kg)", capacity_kg=600.0, speed_kmh=35.0),
        VehicleBase(id=2, name="EcoTruck Heavy 2 (600kg)", capacity_kg=600.0, speed_kmh=35.0),
        VehicleBase(id=3, name="EcoTruck Heavy 3 (600kg)", capacity_kg=600.0, speed_kmh=35.0),
        VehicleBase(id=4, name="EcoTruck Heavy 4 (600kg)", capacity_kg=600.0, speed_kmh=35.0),
        VehicleBase(id=5, name="EcoTruck Heavy 5 (600kg)", capacity_kg=600.0, speed_kmh=35.0),
    ]
    
    return {
        "id": "city_district",
        "name": "City Metropolitan District (40 Points, 5 Trucks)",
        "description": "Large-scale municipal routing with industrial estates, dense markets, and arterial highways.",
        "depot": depot,
        "collection_points": points,
        "vehicles": vehicles
    }

SCENARIOS = {
    "urban_core": get_scenario_urban_core,
    "residential_ward": get_scenario_residential_ward,
    "city_district": get_scenario_city_district
}

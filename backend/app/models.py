from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from app.database import Base

class Depot(Base):
    __tablename__ = "depots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="Central Municipal Waste Depot")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class CollectionPoint(Base):
    __tablename__ = "collection_points"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    waste_demand_kg = Column(Float, nullable=False, default=50.0)
    service_time_min = Column(Float, default=5.0)
    priority = Column(Integer, default=1)  # 1 = normal, 2 = high, 3 = critical
    notes = Column(String(255), default="")

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    capacity_kg = Column(Float, nullable=False, default=500.0)
    max_distance_km = Column(Float, default=100.0)
    speed_kmh = Column(Float, default=35.0)
    emission_factor_kg_co2_per_km = Column(Float, default=0.85)  # Average diesel garbage truck

class OptimizationRun(Base):
    __tablename__ = "optimization_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    scenario_name = Column(String(100), default="Custom Scenario")
    algorithm = Column(String(50), nullable=False)
    total_distance_km = Column(Float, nullable=False)
    total_time_min = Column(Float, nullable=False)
    vehicles_used = Column(Integer, nullable=False)
    total_waste_collected_kg = Column(Float, nullable=False)
    capacity_violations = Column(Integer, default=0)
    execution_time_ms = Column(Float, nullable=False)
    routes_json = Column(JSON, nullable=False)
    metrics_json = Column(JSON, default=dict)

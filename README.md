# 🚛 EcoRoute — Municipal Solid Waste Collection Route Optimization Using CVRP

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React_19-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://react.dev/)
[![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=flat-square&logo=openstreetmap&logoColor=white)](https://www.openstreetmap.org/)
[![OSRM](https://img.shields.io/badge/OSRM-Routing-blue?style=flat-square)](http://project-osrm.org/)
[![Google OR‑Tools](https://img.shields.io/badge/Google_OR--Tools-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/optimization)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

> **EcoRoute** is a CVRP-based municipal waste collection route optimizer that compares a greedy heuristic, Genetic Algorithm, and Google OR-Tools using **real road-network distances obtained through OpenStreetMap and OSRM (Open Source Routing Machine)**.

---

## 📌 1. Problem Statement & Mathematical Formulation

In traditional Municipal Solid Waste Management (MSWM), collection trucks typically traverse uncoordinated or static routes, leading to redundant travel distance, unnecessary fuel consumption, unbalanced truck workloads, and premature payload saturation.

EcoRoute models municipal garbage collection as a **Capacitated Vehicle Routing Problem (CVRP)**, seeking the sequence of collection points and vehicle assignments that minimizes total road distance while strictly satisfying vehicle payload limits.

### Mathematical Formulation

$$\min Z = \sum_{k \in V} \sum_{i \in N} \sum_{j \in N} d_{ij} \cdot x_{ijk}$$

**Subject to:**

1. **Single Visit Requirement** — Every collection bin $j \in C$ must be serviced by exactly one vehicle:
   $$\sum_{k \in V} \sum_{i \in N} x_{ijk} = 1 \quad \forall j \in C$$

2. **Vehicle Payload Limit** — Total waste collected on route $k$ cannot exceed truck capacity $Q$:
   $$\sum_{j \in C} q_j \cdot y_{jk} \le Q \quad \forall k \in V$$

3. **Flow Conservation** — Every truck originates and concludes its journey at the central municipal depot (node 0):
   $$\sum_{j \in C} x_{0jk} = \sum_{i \in C} x_{i0k} \le 1 \quad \forall k \in V$$

Where:
- $V$: Fleet of collection vehicles.
- $C$: Collection bin locations; $N = C \cup \{0\}$ (depot is index 0).
- $d_{ij}$: **Real driving road distance** between locations $i$ and $j$ computed via **OpenStreetMap / OSRM Table Service**.
- $q_j$: Waste demand at location $j$ in kilograms.
- $Q$: Truck payload capacity limit in kilograms.

---

## 🗺️ 2. Real Road Network Routing via OpenStreetMap & OSRM

Unlike simplified models that rely on straight-line Euclidean or Haversine approximations, EcoRoute integrates directly with the **Open Source Routing Machine (OSRM)**:

| OSRM Service | Usage in EcoRoute | API Endpoint |
|---|---|---|
| **Table Service** | Computes the N×N road distance matrix (meters) and driving duration matrix (seconds) for all collection points and the depot in a single query | `/table/v1/driving/{coords}?annotations=distance,duration` |
| **Route Service** | Fetches the actual street-level GeoJSON polyline for each optimized vehicle route, following real roads, turns, one-way systems, and junctions | `/route/v1/driving/{coords}?overview=full&geometries=geojson` |

The system includes a **Haversine geodesic fallback** (with a ×1.28 urban circuity factor) that activates only when the OSRM server is unreachable, ensuring the application always works.

---

## 🧠 3. Optimization Algorithms Evaluated

Under identical road network matrices and capacity constraints, EcoRoute evaluates three algorithmic paradigms:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   CVRP Optimization Architecture                       │
├─────────────────────┬──────────────────────────┬───────────────────────┤
│ Baseline Heuristic  │ Metaheuristic Approach   │ Benchmark Solver      │
├─────────────────────┼──────────────────────────┼───────────────────────┤
│  Nearest Neighbor   │    Genetic Algorithm     │    Google OR-Tools    │
│  • Greedy choice    │    • Permutation Chromo  │    • RoutingModel     │
│  • Fast reference   │    • Order Crossover OX  │    • Guided Local     │
│  • O(N²) complexity │    • 2-Opt Inversion Mut │      Search (GLS)     │
│                     │    • Tournament Selection│    • Near-optimal     │
│                     │    • Elitism (top 8%)    │      benchmark        │
└─────────────────────┴──────────────────────────┴───────────────────────┘
```

### 3.1 Nearest Neighbor (Greedy Baseline)
- Always dispatches the truck to the **nearest unvisited bin** that fits within the remaining vehicle capacity.
- Returns to depot when the truck is full and mobilizes the next vehicle.
- Serves as the unoptimized **"Before"** benchmark for savings measurement.

### 3.2 Genetic Algorithm (Metaheuristic)
- **Representation**: Permutation chromosomes representing node visiting orders, decoded using capacity-constrained vehicle partitioning.
- **Initialization**: Greedy seed (nearest-neighbor tour) + random population (60 individuals).
- **Crossover**: Order Crossover (OX) preserving topological permutations.
- **Mutation**: 2-Opt sub-segment inversion combined with random swap mutation (25% rate).
- **Selection & Elitism**: Tournament selection (size 3) with top 8% elite preservation across 100 generations.
- **Fitness**: Total road distance with heavy penalty (×1000) for unassigned bins.

### 3.3 Google OR-Tools (Optimization Benchmark Solver)
- Formulated via `RoutingIndexManager` and `RoutingModel` with the depot at index 0.
- Uses `SetArcCostEvaluatorOfAllVehicles` over real road distance matrices (converted to integer meters for solver precision).
- Registers an additive **Capacity dimension** with per-vehicle payload limits.
- Solved with initial `PATH_CHEAPEST_ARC` followed by `GUIDED_LOCAL_SEARCH` (GLS) metaheuristic refinement (2-second time limit).
- Allows visit dropping with high penalty (1,000,000) only when fleet capacity is physically insufficient.

---

## 📊 4. Experimental Results Across Problem Scales (OSRM-Measured)

Measured across all three municipal benchmark scenarios using live OpenStreetMap / OSRM road networks:

| Scenario Scale | Collection Bins | Fleet Configuration | Nearest Neighbor (Baseline) | Genetic Algorithm | Google OR-Tools (Benchmark) | Distance Savings vs. Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Urban Commercial Core** | 12 | 3 Trucks × 500 kg | 72.56 km | 62.53 km | **61.82 km** | **−14.8% Saved (−10.74 km)** |
| **Residential Ward** | 25 | 4 Trucks × 500 kg | 117.89 km | 129.89 km | **110.79 km** | **−6.0% Saved (−7.10 km)** |
| **City District** | 40 | 5 Trucks × 600 kg | 158.15 km | 168.52 km | **131.76 km** | **−16.7% Saved (−26.39 km)** |

---

## 🗺️ 5. Municipal Scenario Datasets

All scenarios use **synthetic waste-demand values mapped to realistic geographic coordinates in the Chennai Metropolitan Area**:

1. **Urban Commercial Core** (`backend/data/urban_core.json`):
   - 12 high-density locations (Wholesale Markets, Railway Terminals, Commercial Complexes).
   - 3 collection trucks (500 kg capacity each).
2. **Residential & Market Ward** (`backend/data/residential_ward.json`):
   - 25 locations across residential sectors and community hubs.
   - 4 collection trucks (500 kg capacity each).
3. **City Metropolitan District** (`backend/data/city_district.json`):
   - 40 locations covering industrial estates, residential wards, and arterial roads.
   - 5 collection trucks (600 kg capacity each).

---

## 🏗️ 6. System Architecture

```text
               React 19 + Vite
                     │
            Leaflet + OpenStreetMap
                     │
                  FastAPI
                     │
          ┌──────────┴──────────┐
          │                     │
        OSRM               CVRP Engine
          │                     │
   ┌──────┴──────┐       ┌─────┼─────┐
   │             │       │     │     │
 Table        Route     NN    GA   OR-Tools
   │             │
Distance/    Street-level
Time Matrix  GeoJSON Polylines
                     │
                     ▼
         Optimized Route Visualization
```

- **No database** — all scenario data is loaded from JSON files.
- **No traffic simulation** — distances come directly from OSRM road networks.
- **No authentication** — the application is a single-purpose optimization tool.

---

## 💻 7. Quickstart Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Node.js 18+ (Tested on Node 22)

### 1. Run the Backend API
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --reload
```
> API runs at `http://127.0.0.1:8000`
> Interactive Docs: `http://127.0.0.1:8000/docs`

### 2. Run the React Frontend
```bash
cd frontend
npm install
npm run dev
```
> Web UI runs at `http://localhost:5173`

### 3. Docker (Optional)
```bash
docker compose up --build
```
> Backend: `http://localhost:8000` — Frontend: `http://localhost:5173`

---

## 📂 8. Repository Structure

```text
EcoRoute/
├── backend/
│   ├── app/
│   │   ├── routing/
│   │   │   ├── distance_matrix.py   # OSRM Table + Route integration
│   │   │   ├── nearest_neighbor.py  # Baseline greedy CVRP solver
│   │   │   ├── genetic_algorithm.py # Metaheuristic CVRP solver (100 generations)
│   │   │   ├── ortools_solver.py    # Google OR-Tools benchmark solver (GLS)
│   │   │   └── benchmarks.py        # Before-vs-After savings comparison engine
│   │   ├── routes/
│   │   │   └── api.py               # FastAPI REST endpoints
│   │   ├── config.py                # OSRM router endpoint configuration
│   │   ├── schemas.py               # Pydantic request/response models
│   │   ├── scenarios.py             # JSON dataset loader
│   │   └── main.py                  # FastAPI application entrypoint
│   ├── data/
│   │   ├── urban_core.json          # 12-point commercial scenario
│   │   ├── residential_ward.json    # 25-point residential scenario
│   │   └── city_district.json       # 40-point metropolitan scenario
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapComponent.jsx     # Leaflet map with OSRM street polylines
│   │   │   ├── SidebarControls.jsx  # Fleet configuration & truck route manifest
│   │   │   └── ComparisonCards.jsx  # KPI savings cards & benchmark comparison table
│   │   ├── App.jsx                  # Main application orchestrator
│   │   ├── index.css                # Enterprise design system
│   │   └── main.jsx                 # React root mount
│   ├── index.html
│   ├── nginx.conf
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 📡 9. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health check and supported algorithms |
| `GET` | `/api/scenarios` | List all available municipal scenarios |
| `GET` | `/api/scenarios/{id}` | Retrieve full scenario data (depot, points, vehicles) |
| `POST` | `/api/optimize` | Run a single algorithm (`nearest_neighbor`, `genetic_algorithm`, `ortools`, or `all`) |
| `POST` | `/api/benchmark` | Run all three algorithms and return comparative savings metrics |

---

## 🎓 10. Academic Coursework Reference

- **Course**: Municipal Solid Waste Management (MSWM) — Open Elective
- **Domain**: Computer Science and Engineering / Route Optimization & Operations Research
- **Repository**: [github.com/Vineesh-12/EcoRoute](https://github.com/Vineesh-12/EcoRoute)
- **Author**: Vineesh (`vineeshreddy4@gmail.com`)

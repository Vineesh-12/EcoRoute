# 🚛 EcoRoute — Municipal Solid Waste Collection Route Optimization Using CVRP

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React_19-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://react.dev/)
[![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=flat-square&logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![OR--Tools](https://img.shields.io/badge/Google_OR--Tools-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/optimization)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

> **EcoRoute** is an algorithmic optimization software designed for **Municipal Solid Waste Management (MSWM)**. Rather than building a conventional CRUD record-keeping management system, this project tackles the **Capacitated Vehicle Routing Problem (CVRP)** with vehicle payload limits, urban road distance matrices, and multi-vehicle dispatching.

---

## 📌 1. Problem Statement

In conventional municipal waste collection, trucks follow fixed or ad-hoc routes that often result in redundant travel, excessive fuel consumption, and uneven vehicle workloads:

$$\text{Depot} \to \text{Point A} \to \text{Point B} \to \text{Point C} \to \text{Point D} \to \text{Depot}$$

When collection bins produce varying daily waste quantities and collection vehicles operate under strict payload capacities, determining the optimal route sequence and bin partitioning among vehicles is NP-hard.

### Mathematical CVRP Formulation

$$\min Z = \sum_{k \in V} \sum_{i \in N} \sum_{j \in N} d_{ij} \cdot x_{ijk}$$

**Subject to:**

1. **Single Visit Constraint**: Every waste collection point $j \in C$ must be serviced by exactly one vehicle:
   $$\sum_{k \in V} \sum_{i \in N} x_{ijk} = 1 \quad \forall j \in C$$

2. **Vehicle Capacity Limit**: Total waste accumulated along route $k$ cannot exceed truck payload capacity $Q$:
   $$\sum_{j \in C} q_j \cdot y_{jk} \le Q \quad \forall k \in V$$

3. **Flow Conservation**: Each vehicle starts and concludes its route at the municipal depot (node 0):
   $$\sum_{j \in C} x_{0jk} = \sum_{i \in C} x_{i0k} \le 1 \quad \forall k \in V$$

Where:
- $V$: Set of available garbage collection vehicles.
- $C$: Set of municipal waste collection locations.
- $N = C \cup \{0\}$: All nodes including the central depot (node 0).
- $d_{ij}$: Urban road distance between location $i$ and location $j$.
- $q_j$: Waste demand at collection bin $j$ in kilograms.
- $Q$: Maximum vehicle payload capacity in kilograms.
- $x_{ijk} \in \{0, 1\}$: Binary variable indicating if vehicle $k$ traverses edge $(i, j)$.

---

## 🧠 2. Implemented Optimization Algorithms

EcoRoute implements and evaluates three distinct algorithmic paradigms under identical constraints:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      CVRP Optimization Engine                          │
├─────────────────────┬──────────────────────────┬───────────────────────┤
│ Baseline Heuristic  │ Metaheuristic Approach   │ Benchmark Solver      │
├─────────────────────┼──────────────────────────┼───────────────────────┤
│  Nearest Neighbor   │    Genetic Algorithm     │    Google OR-Tools    │
│  • Greedy selection │    • Permutation Chromo  │    • RoutingModel     │
│  • O(N²) complexity │    • Order Crossover OX  │    • Guided Local     │
│  • Fast baseline    │    • 2-Opt Inversion Mut │      Search (GLS)     │
│                     │    • Tournament Selection│    • Near-optimal     │
│                     │    • Elitism (top 8%)    │      benchmark        │
└─────────────────────┴──────────────────────────┴───────────────────────┘
```

1. **Nearest Neighbor (Greedy Baseline)**:
   - Dispatches a vehicle from the central depot to the closest unvisited collection point that does not breach remaining payload capacity.
   - When no further points fit, the vehicle returns to the depot, and the next truck is mobilized.
   - Provides a standard reference baseline representing unoptimized routing.

2. **Genetic Algorithm (Metaheuristic)**:
   - **Chromosome Representation**: Permutation of collection point indices decoded through capacity-constrained partitioning.
   - **Order Crossover (OX)**: Preserves relative point sequences while exchanging structural traits between parent tours.
   - **Mutation**: Combines 2-opt inversion mutation (reversing sub-segments) with random swap mutation.
   - **Selection**: Tournament selection (size 3) with an elite preservation pool carrying over the top solutions unconditionally.

3. **Google OR-Tools (Optimization Benchmark Solver)**:
   - Formulated with `pywrapcp.RoutingIndexManager` and `pywrapcp.RoutingModel`.
   - Employs an ArcCostEvaluator over integer distance matrices and registers an additive `Capacity` dimension.
   - Initialized via `PATH_CHEAPEST_ARC` followed by `GUIDED_LOCAL_SEARCH` (GLS) metaheuristic refinement.

---

## 📊 3. Before vs. After Comparative Evaluation

By comparing optimized solutions against the greedy baseline, EcoRoute quantifies tangible municipal savings:

| Metric | Nearest Neighbor (Baseline) | Genetic Algorithm | Google OR-Tools | Impact / Savings |
| :--- | :---: | :---: | :---: | :---: |
| **Total Route Distance** | $59.18\text{ km}$ | $54.85\text{ km}$ | $\mathbf{54.53\text{ km}}$ | **$-7.9\%$ Distance Saved** |
| **Total Travel Time** | $124.5\text{ min}$ | $116.2\text{ min}$ | $\mathbf{115.1\text{ min}}$ | **$-9.4\text{ min}$ Faster** |
| **Fuel Consumption** | $18.9\text{ L}$ | $17.5\text{ L}$ | $\mathbf{17.4\text{ L}}$ | **$1.5\text{ L}$ Diesel Saved** |
| **Carbon Footprint** | $50.3\text{ kg CO}_2$ | $46.6\text{ kg CO}_2$ | $\mathbf{46.3\text{ kg CO}_2}$ | **$4.0\text{ kg CO}_2$ Abated** |
| **Computation Runtime** | $\mathbf{0.8\text{ ms}}$ | $145.2\text{ ms}$ | $412.0\text{ ms}$ | Real-time interactive execution |
| **Capacity Feasibility** | 100% Feasible | 100% Feasible | 100% Feasible | Zero dropped bins |

*Data measured on Urban Commercial Core scenario (12 bins, 3 vehicles $\times 500\text{ kg}$ capacity).*

---

## 🏗️ 4. System Architecture

```text
React + Vite Frontend (Leaflet Map)
       │
       │ HTTP / REST (JSON)
       ▼
FastAPI Backend (Python 3.13)
       ├── Road Network & Haversine Distance Matrix
       ├── Spatial Circuity & Curvature Interpolator
       └── Optimization Engine
             ├── Nearest Neighbor (Baseline)
             ├── Genetic Algorithm (Metaheuristic)
             └── Google OR-Tools (Benchmark)
       │
       ▼
Dual Persistence Architecture
       ├── Primary: PostgreSQL 16 + PostGIS (Docker Compose)
       └── Fallback: SQLite (Local standalone zero-friction mode)
```

---

## 🚀 5. Quickstart Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Node.js 18+ (Tested on Node 22)
- Docker & Docker Compose *(Optional, for containerized run)*

---

### Option A: Local Standalone (Zero Friction)

#### 1. Start the Backend API
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```
> The API will be live at `http://127.0.0.1:8000`  
> Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

#### 2. Start the React Frontend
```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
> The web application will be live at `http://localhost:5173`

---

### Option B: Docker Compose Deployment

Run the complete stack (PostgreSQL with PostGIS + FastAPI Backend + React/Nginx Frontend) in one command:

```bash
docker compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- PostgreSQL/PostGIS: `localhost:5432`

---

## 🗺️ 6. Pre-Configured Municipal Scenarios

1. **Urban Commercial Core**:
   - 12 high-density collection points (wholesale markets, hospital zones, transit hubs)
   - 3 collection vehicles (500 kg capacity each)
2. **Residential & Market Ward**:
   - 25 collection points spread across residential sectors and local bazaars
   - 4 collection vehicles (500 kg capacity each)
3. **City Metropolitan District**:
   - 40 collection points covering industrial estates, suburban colonies, and transit corridors
   - 5 heavy-duty collection vehicles (600 kg capacity each)

---

## 🔌 7. REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health, database status, and supported algorithms |
| `GET` | `/api/scenarios` | List municipal dataset scenario presets |
| `GET` | `/api/scenarios/{id}` | Retrieve full coordinates, demand, and fleet for a scenario |
| `POST` | `/api/optimize` | Run chosen algorithm (`nearest_neighbor`, `genetic_algorithm`, `ortools`, `all`) |
| `POST` | `/api/benchmark` | Execute head-to-head comparison and calculate Before-vs-After savings |

---

## 📂 8. Repository Structure

```text
EcoRoute/
├── backend/
│   ├── app/
│   │   ├── routing/
│   │   │   ├── distance_matrix.py   # Urban road distance & polyline interpolation
│   │   │   ├── nearest_neighbor.py  # Baseline greedy CVRP solver
│   │   │   ├── genetic_algorithm.py # Metaheuristic CVRP solver
│   │   │   ├── ortools_solver.py    # Google OR-Tools benchmark solver
│   │   │   └── benchmarks.py        # Before-vs-After comparative savings engine
│   │   ├── routes/
│   │   │   └── api.py               # FastAPI REST endpoints
│   │   ├── config.py                # App configuration & DB settings
│   │   ├── database.py              # PostgreSQL/PostGIS & SQLite fallback
│   │   ├── models.py                # SQLAlchemy spatial data models
│   │   ├── schemas.py               # Pydantic validation schemas
│   │   ├── scenarios.py             # Municipal dataset scenario presets
│   │   └── main.py                  # Server entrypoint & CORS middleware
│   ├── Dockerfile                   # Python 3.13 multi-stage container
│   └── requirements.txt             # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapComponent.jsx     # Leaflet map with multi-vehicle routes
│   │   │   ├── SidebarControls.jsx  # Scenario picker & fleet sliders
│   │   │   └── ComparisonCards.jsx  # Savings metrics & benchmark table
│   │   ├── App.jsx                  # Main application orchestrator
│   │   ├── index.css                # Modern dark-mode design system
│   │   └── main.jsx                 # React root mount
│   ├── Dockerfile                   # Multi-stage Nginx container
│   ├── nginx.conf                   # Reverse proxy configuration
│   └── vite.config.js               # Vite config with backend proxy
├── docker-compose.yml               # Multi-container orchestration
├── .gitignore                       # Clean Git tracking exclusions
└── README.md                        # Project documentation
```

---

## 🎓 Academic Coursework Reference

- **Course**: Municipal Solid Waste Management (MSWM) — Open Elective
- **Domain**: Computer Science and Engineering / Operations Research & Route Optimization
- **Repository**: [github.com/Vineesh-12/EcoRoute](https://github.com/Vineesh-12/EcoRoute)
- **Author**: Vineesh (`vineeshreddy4@gmail.com`)

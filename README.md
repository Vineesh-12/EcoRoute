# 🚛 EcoRoute — Municipal Solid Waste Collection Route Optimization Using CVRP

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-46E3B7?style=flat-square&logo=render&logoColor=white)](https://ecoroute-1ydb.onrender.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React_19-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://react.dev/)
[![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=flat-square&logo=openstreetmap&logoColor=white)](https://www.openstreetmap.org/)
[![OSRM](https://img.shields.io/badge/OSRM-Routing-blue?style=flat-square)](http://project-osrm.org/)
[![Google OR‑Tools](https://img.shields.io/badge/Google_OR--Tools-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/optimization)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

> **EcoRoute** is an engineering-focused municipal solid waste collection route optimizer. It models waste collection as a **Capacitated Vehicle Routing Problem (CVRP)** and evaluates three distinct algorithmic paradigms—a greedy heuristic (**Nearest Neighbor**), a metaheuristic (**Genetic Algorithm**), and an industrial mathematical programming solver (**Google OR-Tools**)—using **real street-network distances and driving durations obtained from OpenStreetMap and the Open Source Routing Machine (OSRM)**.

---

### 🌐 Live Deployment

| Resource | Link |
|---|---|
| **Live Web Application** | **[https://ecoroute-1ydb.onrender.com](https://ecoroute-1ydb.onrender.com/)** |
| **Interactive OpenAPI Documentation** | **[https://ecoroute-1ydb.onrender.com/docs](https://ecoroute-1ydb.onrender.com/docs)** |
| **API Health Status** | **[https://ecoroute-1ydb.onrender.com/api/health](https://ecoroute-1ydb.onrender.com/api/health)** |

---

## 📌 1. Problem Statement & Mathematical Formulation

In conventional Municipal Solid Waste Management (MSWM), collection trucks typically operate on ad-hoc or static historical schedules. This results in:
- Excessive and redundant transit mileage.
- Elevated fuel expenditure and greenhouse gas emissions.
- Severe workload imbalance across vehicles in the fleet.
- Premature vehicle payload saturation requiring inefficient mid-shift depot trips.

EcoRoute formalizes this challenge as a **Capacitated Vehicle Routing Problem (CVRP)**, seeking the sequence of collection stops and vehicle assignments that minimizes total fleet travel distance over actual road networks while strictly respecting truck capacity constraints.

### Mathematical Formulation

$$\min Z = \sum_{k \in V} \sum_{i \in N} \sum_{j \in N} d_{ij} \cdot x_{ijk}$$

**Subject to:**

1. **Single-Visit Constraint** — Every collection node $j \in C$ must be serviced by exactly one vehicle:
   $$\sum_{k \in V} \sum_{i \in N} x_{ijk} = 1 \quad \forall j \in C$$

2. **Payload Capacity Constraint** — Total waste collected along route $k$ cannot exceed truck payload capacity $Q$:
   $$\sum_{j \in C} q_j \cdot y_{jk} \le Q \quad \forall k \in V$$

3. **Flow Conservation & Depot Return** — Every active truck departs from and returns to the central municipal depot (node 0):
   $$\sum_{j \in C} x_{0jk} = \sum_{i \in C} x_{i0k} \le 1 \quad \forall k \in V$$

Where:
- $V$: Set of available collection vehicles $\{1, 2, \dots, K\}$.
- $C$: Set of waste collection points; $N = C \cup \{0\}$ where node $0$ denotes the municipal depot.
- $d_{ij}$: **Real driving road distance** between locations $i$ and $j$ obtained from **OSRM Table Service**.
- $q_j$: Waste demand at location $j$ (in kg).
- $Q$: Maximum vehicle payload capacity (in kg).
- $x_{ijk} \in \{0, 1\}$: Binary decision variable equal to $1$ if vehicle $k$ traverses edge $(i, j)$, and $0$ otherwise.
- $y_{jk} \in \{0, 1\}$: Binary decision variable indicating whether collection point $j$ is serviced by vehicle $k$.

---

## 🗺️ 2. Real Road Network Routing via OpenStreetMap & OSRM

Simplified CVRP literature often assumes straight-line Euclidean distance or Haversine arc distance, both of which severely underestimate actual travel by ignoring road geometry, one-way streets, bridges, and dead ends.

EcoRoute resolves this by integrating directly with the **Open Source Routing Machine (OSRM)** running on OpenStreetMap data:

| OSRM Service | Role in EcoRoute | Query Pattern |
|---|---|---|
| **Table Service** | Computes the full asymmetric $N \times N$ road distance matrix (meters) and driving duration matrix (seconds) in a single batched HTTP call. | `/table/v1/driving/{lon,lat;...}?annotations=distance,duration` |
| **Route Service** | Fetches high-resolution street-level GeoJSON polylines for each optimized vehicle tour to render exact driving paths on the Leaflet map. | `/route/v1/driving/{lon,lat;...}?overview=full&geometries=geojson` |

> **Fault Tolerance:** If the public OSRM router is unreachable or throttled, EcoRoute automatically falls back to an internal Haversine geodesic distance engine calibrated with an urban circuity factor ($\times 1.28$), ensuring uninterrupted operation.

---

## 🧠 3. Optimization Algorithms Evaluated

EcoRoute benchmarks three distinct algorithmic strategies on identical road matrices and fleet constraints:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   CVRP Optimization Architecture                       │
├─────────────────────┬──────────────────────────┬───────────────────────┤
│ Baseline Heuristic  │ Metaheuristic Approach   │ Benchmark Solver      │
├─────────────────────┼──────────────────────────┼───────────────────────┤
│  Nearest Neighbor   │    Genetic Algorithm     │    Google OR-Tools    │
│  • Greedy selection │    • Permutation Chromo  │    • RoutingModel     │
│  • Fast baseline    │    • Order Crossover OX  │    • Guided Local     │
│  • O(N²) complexity │    • 2-Opt Inversion Mut │      Search (GLS)     │
│                     │    • Tournament Selection│    • Near-optimal     │
│                     │    • Elitism (top 8%)    │      benchmark        │
└─────────────────────┴──────────────────────────┴───────────────────────┘
```

### 3.1 Nearest Neighbor (Greedy Baseline)
- **Concept:** Dispatches a vehicle from the depot to the nearest unvisited collection point whose demand does not exceed remaining capacity. When no eligible bin can be added without violating capacity, the truck returns to the depot, and the next truck is dispatched.
- **Role:** Serves as the unoptimized baseline reflecting typical intuitive dispatch practices, providing the reference point for calculating distance and fuel savings.

### 3.2 Genetic Algorithm (Population-Based Metaheuristic)
- **Chromosome Representation:** Permutation of collection node indices, decoded into distinct vehicle routes via capacity-constrained partition.
- **Seeding:** Hybrid initialization using 1 greedy Nearest Neighbor seed plus 59 randomly shuffled individuals (population size $N=60$).
- **Crossover:** **Order Crossover (OX)**, which preserves contiguous subsequence adjacency and prevents invalid offspring permutations.
- **Mutation:** **2-Opt sub-tour inversion** combined with random pairwise swaps (25% mutation rate) to escape local minima.
- **Selection & Survival:** Tournament selection ($k=3$) with strict elitism preserving the top 8% fittest chromosomes across 100 generations.
- **Objective Function:** Total road network travel distance with an escalating penalty ($\times 1000$) for any unserviced bins.

### 3.3 Google OR-Tools (Industrial Operations Research Solver)
- **Formulation:** Built using OR-Tools' `RoutingIndexManager` and `RoutingModel` with node $0$ fixed as the vehicle depot.
- **Cost Evaluator:** Arc costs evaluated directly from the integer-meter OSRM road distance matrix (`SetArcCostEvaluatorOfAllVehicles`).
- **Dimension Constraints:** Additive `Capacity` dimension enforcing cumulative vehicle payload bounds with zero slack at the depot.
- **Search Strategy:** First-solution strategy using `PATH_CHEAPEST_ARC`, followed by metaheuristic local search via **`GUIDED_LOCAL_SEARCH` (GLS)** with a 2-second wall-clock time limit.
- **Role:** Represents the theoretical near-optimal benchmark against which the heuristic and metaheuristic approaches are validated.

---

## 📊 4. Empirical Benchmark Results (OSRM-Verified)

Evaluated across three realistic municipal scenarios in the Chennai metropolitan area using live OpenStreetMap / OSRM road networks:

| Scenario | Bins | Fleet Configuration | Nearest Neighbor (Baseline) | Genetic Algorithm | Google OR-Tools (Benchmark) | Distance Reduction vs. Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Urban Commercial Core** | 12 | 3 Trucks × 500 kg | 72.56 km | 62.31 km | **61.82 km** | **−14.8% Saved (−10.74 km)** |
| **Residential Ward** | 25 | 4 Trucks × 500 kg | 117.89 km | 131.97 km | **110.79 km** | **−6.0% Saved (−7.10 km)** |
| **City Metropolitan District** | 40 | 5 Trucks × 600 kg | 158.15 km | 201.18 km | **131.76 km** | **−16.7% Saved (−26.39 km)** |

### Key Observations:
1. **Google OR-Tools** consistently achieved the shortest overall distance across all scales, delivering between **6.0% and 16.7% mileage reductions** compared to the greedy baseline.
2. The **Genetic Algorithm** outperformed Nearest Neighbor on the compact 12-bin scenario (−14.1% reduction) and closely mirrored OR-Tools. On larger permutations (25–40 bins), the 100-generation GA demonstrated exploratory behavior within the vast combinatorial search space ($40! \approx 8.16 \times 10^{47}$).
3. **Street-network awareness** eliminated unrealistic shortcuts that straight-line routing models produce around one-way streets, rail crossings, and coastal road bends in Chennai.

---

## 🗺️ 5. Municipal Scenario Datasets

All collection points are mapped to genuine road coordinates in Chennai, Tamil Nadu, India:

1. **Urban Commercial Core** (`backend/data/urban_core.json`):
   - **Scale:** 12 collection bins across high-density wholesale markets, transit hubs, and commercial zones (Koyambedu, George Town, T. Nagar).
   - **Fleet:** 3 collection trucks (500 kg payload capacity each).
2. **Residential & Market Ward** (`backend/data/residential_ward.json`):
   - **Scale:** 25 collection points spanning residential neighborhoods, community markets, and schools (Mylapore, Adyar, Alwarpet, Mandaveli).
   - **Fleet:** 4 collection trucks (500 kg payload capacity each).
3. **City Metropolitan District** (`backend/data/city_district.json`):
   - **Scale:** 40 collection points covering a broad urban swath including industrial parks, major hospitals, and arterial collection bins (Guindy, Anna Nagar, Velachery, OMR).
   - **Fleet:** 5 collection trucks (600 kg payload capacity each).

---

## 🏗️ 6. System Architecture

```text
┌───────────────────────────────────────────────────────────┐
│              Client Browser (React 19 + Vite)             │
│   • Leaflet Interactive Map    • Route Comparison Table   │
│   • Real-Time KPI Cards        • Vehicle Route Manifest   │
└─────────────────────────────┬─────────────────────────────┘
                              │ HTTP / REST
                              ▼
┌───────────────────────────────────────────────────────────┐
│                   FastAPI Backend Service                 │
│   • Scenario Loader            • CVRP Dispatcher          │
│   • SPA Static File Server     • OpenAPI Documentation    │
└──────────────┬─────────────────────────────┬──────────────┘
               │                             │
               ▼                             ▼
┌─────────────────────────────┐ ┌───────────────────────────┐
│   OSRM Routing Service      │ │       CVRP Engine         │
│  • Table API (NxN Matrix)   │ │  • Nearest Neighbor       │
│  • Route API (GeoJSON Path) │ │  • Genetic Algorithm      │
│  • Haversine Fallback       │ │  • Google OR-Tools (GLS)  │
└─────────────────────────────┘ └───────────────────────────┘
```

- **Clean Decoupled Architecture:** Stateless backend; all scenario definitions reside in versioned JSON data files.
- **Zero Overhead:** No external database or authentication layers required.
- **Production Monolith Deployment:** On Render, the FastAPI backend mounts and serves the pre-built React SPA static bundle, providing a unified single-URL deployment.

---

## 🚀 7. Deployment Architecture (Render)

EcoRoute is configured for turnkey single-service deployment on **Render**:

```text
Git Push to GitHub (main)
        │
        ▼
Render Web Service Triggered
        │
        ├── Executes: ./build.sh
        │     ├── Installs Python dependencies (pip install -r backend/requirements.txt)
        │     ├── Installs Node dependencies (npm install in frontend/)
        │     ├── Builds production bundle (npm run build -> frontend/dist/)
        │     └── Copies dist/ -> backend/static/
        │
        └── Starts: uvicorn app.main:app --host 0.0.0.0 --port $PORT
              ├── Mounts /static for CSS, JS, and assets
              ├── Serves index.html at root route /
              └── Serves REST API at /api/* and Swagger UI at /docs
```

Configuration files:
- [`render.yaml`](render.yaml): Infrastructure-as-code declaration specifying runtime, environment variables, and build pipeline.
- [`build.sh`](build.sh): Automated unified build script.

---

## 💻 8. Local Setup & Execution

### Prerequisites
- **Python 3.10+** (Tested on Python 3.13)
- **Node.js 18+** (Tested on Node 22)
- **Git**

### Option A: Local Development Server

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Vineesh-12/EcoRoute.git
   cd EcoRoute
   ```

2. **Run the Backend API:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --port 8000 --reload
   ```
   - API endpoints: `http://localhost:8000`
   - Interactive Swagger docs: `http://localhost:8000/docs`

3. **Run the Frontend Development Server:**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```
   - Web application: `http://localhost:5173`

---

### Option B: Docker Compose (One-Command Launch)

```bash
docker compose up --build
```
- Frontend UI: `http://localhost:5173`
- Backend API: `http://localhost:8000`

---

## 📂 9. Repository Structure

```text
EcoRoute/
├── .gitignore
├── build.sh                         # Unified build script for production deployment
├── docker-compose.yml               # Multi-container orchestration (dev)
├── README.md                        # Master project documentation
├── render.yaml                      # Render Blueprint infrastructure specification
├── backend/
│   ├── Dockerfile                   # Container definition for backend service
│   ├── requirements.txt             # Minimal Python dependencies
│   ├── app/
│   │   ├── config.py                # OSRM router endpoint configuration
│   │   ├── main.py                  # FastAPI app entrypoint & SPA static mount
│   │   ├── scenarios.py             # JSON scenario loader
│   │   ├── schemas.py               # Pydantic request/response data contracts
│   │   ├── routes/
│   │   │   └── api.py               # REST endpoints (/optimize, /benchmark, /scenarios)
│   │   └── routing/
│   │       ├── distance_matrix.py   # OSRM Table + Route client with Haversine fallback
│   │       ├── nearest_neighbor.py  # Greedy CVRP heuristic
│   │       ├── genetic_algorithm.py # Permutation metaheuristic (OX crossover, 2-opt)
│   │       ├── ortools_solver.py    # Google OR-Tools CVRP solver (GLS)
│   │       └── benchmarks.py        # Comparative evaluation engine
│   └── data/
│       ├── urban_core.json          # 12-point Chennai commercial scenario
│       ├── residential_ward.json    # 25-point Chennai residential scenario
│       └── city_district.json       # 40-point Chennai metropolitan scenario
└── frontend/
    ├── public/
    │   └── favicon.svg              # EcoRoute brand SVG favicon
    ├── Dockerfile                   # Container definition for frontend service
    ├── index.html                   # HTML5 shell
    ├── nginx.conf                   # Nginx reverse proxy config for Docker
    ├── package.json                 # Node.js dependencies and scripts
    ├── vite.config.js               # Vite build configuration
    └── src/
        ├── App.jsx                  # Root state coordinator
        ├── index.css                # Enterprise design system & tokens
        ├── main.jsx                 # React root mount
        └── components/
            ├── ComparisonCards.jsx  # KPI metrics & multi-algorithm benchmark table
            ├── MapComponent.jsx     # Leaflet map rendering OSRM street polylines
            └── SidebarControls.jsx  # Scenario selector, fleet manifest & run controls
```

---

## 📡 10. REST API Reference

All endpoints are accessible locally or against the live deployment at `https://ecoroute-1ydb.onrender.com/`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check, OSRM status, and supported solvers. |
| `GET` | `/api/scenarios` | Lists metadata for all three pre-configured municipal scenarios. |
| `GET` | `/api/scenarios/{id}` | Retrieves full scenario geometry, bins, coordinates, and fleet capacity. |
| `POST` | `/api/optimize` | Runs a selected CVRP algorithm (`nearest_neighbor`, `genetic_algorithm`, or `ortools`). |
| `POST` | `/api/benchmark` | Concurrently runs all three algorithms on the scenario and returns comparative savings metrics. |

### Example Request: Run Comparative Benchmark

```bash
curl -X POST "https://ecoroute-1ydb.onrender.com/api/benchmark" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "urban_core"
  }'
```

---

## 📄 License & Author

- **Author:** Vineesh ([vineeshreddy4@gmail.com](mailto:vineeshreddy4@gmail.com))
- **Repository:** [github.com/Vineesh-12/EcoRoute](https://github.com/Vineesh-12/EcoRoute)
- **License:** This project is licensed under the [MIT License](LICENSE).

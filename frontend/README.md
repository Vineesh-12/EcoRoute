# EcoRoute — Frontend Client

Interactive mapping interface and benchmark analytics dashboard built with **React 19**, **Vite**, and **Leaflet**.

## Overview

The frontend client serves as the user-facing operations control panel for EcoRoute. It visualizes collection routes on an interactive OpenStreetMap canvas using real street polylines computed by OSRM and displays real-time optimization KPIs.

## Key Features

- **Interactive Leaflet Map (`MapComponent.jsx`)**: Renders collection bins (with demand tooltips), the municipal depot, and color-coded vehicle routes using high-resolution street geometry.
- **Fleet Controls & Manifest (`SidebarControls.jsx`)**: Allows scenario selection, algorithm selection, and displays individual vehicle payload manifests.
- **Benchmark Analytics (`ComparisonCards.jsx`)**: Computes and displays distance savings, fuel reduction estimates, and a multi-algorithm comparative table.

## Development Scripts

```bash
# Install dependencies
npm install

# Start Vite dev server with Hot Module Replacement
npm run dev

# Run Oxlint
npm run lint

# Compile production bundle to dist/
npm run build
```

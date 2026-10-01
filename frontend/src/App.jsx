import React, { useState, useEffect } from 'react';
import { Truck, Activity, RefreshCw } from 'lucide-react';
import MapComponent from './components/MapComponent';
import SidebarControls from './components/SidebarControls';
import ComparisonCards from './components/ComparisonCards';

const API_BASE = '/api';

export default function App() {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState('urban_core');
  const [scenarioData, setScenarioData] = useState(null);

  // Fleet settings
  const [truckCount, setTruckCount] = useState(3);
  const [truckCapacity, setTruckCapacity] = useState(500);

  // Optimization state
  const [loading, setLoading] = useState(false);
  const [comparisonData, setComparisonData] = useState(null);
  const [activeAlgorithm, setActiveAlgorithm] = useState('ortools');
  const [selectedVehicleIndex, setSelectedVehicleIndex] = useState(null);
  const [serverStatus, setServerStatus] = useState('Connecting...');

  // 1. Fetch available scenarios & health on mount
  useEffect(() => {
    fetchHealth();
    fetchScenarios();
  }, []);

  const fetchHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) {
        const data = await res.json();
        setServerStatus(`${data.database}`);
      } else {
        setServerStatus('Offline');
      }
    } catch {
      setServerStatus('Offline');
    }
  };

  const fetchScenarios = async () => {
    try {
      const res = await fetch(`${API_BASE}/scenarios`);
      if (res.ok) {
        const list = await res.json();
        setScenarios(list);
        if (list.length > 0) {
          loadScenario(list[0].id);
        }
      }
    } catch (err) {
      console.error('Failed to load scenarios', err);
    }
  };

  const loadScenario = async (scId) => {
    setSelectedScenarioId(scId);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/scenarios/${scId}`);
      if (res.ok) {
        const data = await res.json();
        setScenarioData(data);
        setTruckCount(data.vehicles.length);
        if (data.vehicles.length > 0) {
          setTruckCapacity(data.vehicles[0].capacity_kg);
        }
        // Run initial optimization comparison automatically for instant visualization
        runComparison(data, data.vehicles.length, data.vehicles[0]?.capacity_kg || 500);
      }
    } catch (err) {
      console.error('Failed to load scenario details', err);
    } finally {
      setLoading(false);
    }
  };

  const runComparison = async (data = scenarioData, count = truckCount, cap = truckCapacity) => {
    if (!data) return;
    setLoading(true);

    // Build vehicle array
    const vehicles = Array.from({ length: count }, (_, i) => ({
      id: i + 1,
      name: `EcoTruck ${i + 1} (${cap}kg)`,
      capacity_kg: cap,
      max_distance_km: 120.0,
      speed_kmh: 35.0,
    }));

    const payload = {
      depot: data.depot,
      collection_points: data.collection_points,
      vehicles: vehicles,
      algorithm: 'all',
      weights: { distance: 1.0, time: 0.0, vehicles: 0.0 },
      traffic_factor: 1.0,
    };

    try {
      const res = await fetch(`${API_BASE}/benchmark`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const comp = await res.json();
        setComparisonData(comp);
        setActiveAlgorithm(comp.best_algorithm || 'ortools');
        setSelectedVehicleIndex(null);
      }
    } catch (err) {
      console.error('Optimization benchmark failed', err);
    } finally {
      setLoading(false);
    }
  };

  const activeResult =
    comparisonData && comparisonData.comparison_summary
      ? comparisonData.comparison_summary[activeAlgorithm]
      : null;

  return (
    <div className="app-container">
      {/* Top Navigation Bar */}
      <header className="header-bar">
        <div className="brand-wrapper">
          <div className="brand-logo">
            <Truck size={22} color="white" />
          </div>
          <div>
            <div className="brand-title">EcoRoute</div>
            <div className="brand-subtitle">
              Smart Municipal Waste Collection Route Optimization (CVRP)
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              fontSize: '0.78rem',
              color: '#94a3b8',
              background: 'rgba(255,255,255,0.04)',
              padding: '0.35rem 0.75rem',
              borderRadius: '9999px',
              border: '1px solid rgba(255,255,255,0.08)',
            }}
          >
            <Activity size={13} color="#10b981" />
            <span>Database: <strong>{serverStatus}</strong></span>
          </div>

          <a
            href="https://github.com/Vineesh-12/EcoRoute"
            target="_blank"
            rel="noreferrer"
            className="btn btn-secondary"
            style={{ padding: '0.45rem 0.85rem', fontSize: '0.78rem' }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
            <span>GitHub Repository</span>
          </a>
        </div>
      </header>

      {/* Main Grid View */}
      <main className="dashboard-grid">
        {/* Left Column: Sidebar Controls */}
        <SidebarControls
          scenarios={scenarios}
          selectedScenarioId={selectedScenarioId}
          onSelectScenario={loadScenario}
          scenarioData={scenarioData}
          truckCount={truckCount}
          setTruckCount={setTruckCount}
          truckCapacity={truckCapacity}
          setTruckCapacity={setTruckCapacity}
          onRunOptimization={() => runComparison()}
          loading={loading}
          activeResult={activeResult}
          selectedVehicleIndex={selectedVehicleIndex}
          onSelectVehicle={setSelectedVehicleIndex}
        />

        {/* Right Column: Map Visualization & Comparative Analytics */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Map View */}
          <div className="glass-panel" style={{ padding: '1rem' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '0.75rem',
              }}
            >
              <div>
                <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                  Active Visualization Algorithm:
                </span>{' '}
                <strong style={{ color: '#10b981', fontSize: '0.92rem' }}>
                  {activeResult?.algorithm_name || 'Loading routes...'}
                </strong>
              </div>

              {activeResult && (
                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Total Route Distance: <strong>{activeResult.total_distance_km} km</strong>{' '}
                  • Travel Time: <strong>{activeResult.total_time_min} min</strong>
                </div>
              )}
            </div>

            <MapComponent
              depot={scenarioData?.depot}
              points={scenarioData?.collection_points}
              activeResult={activeResult}
              selectedVehicleIndex={selectedVehicleIndex}
            />
          </div>

          {/* Comparative Analytics & Before vs After Impact */}
          <ComparisonCards
            comparisonData={comparisonData}
            activeAlgorithm={activeAlgorithm}
            onSelectAlgorithm={setActiveAlgorithm}
          />
        </div>
      </main>
    </div>
  );
}

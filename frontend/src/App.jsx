import React, { useState, useEffect } from 'react';
import { Truck, Download, ExternalLink, MapPin } from 'lucide-react';
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

  // 1. Fetch available scenarios on mount
  useEffect(() => {
    fetchScenarios();
  }, []);

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
        // Run initial optimization comparison automatically
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

    const vehicles = Array.from({ length: count }, (_, i) => ({
      id: i + 1,
      name: `Truck ${i + 1}`,
      capacity_kg: cap,
      max_distance_km: 120.0,
      speed_kmh: 35.0,
    }));

    const payload = {
      depot: data.depot,
      collection_points: data.collection_points,
      vehicles: vehicles,
      algorithm: 'all',
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

  // Export Dispatch Report to JSON
  const handleExportReport = () => {
    if (!comparisonData) return;
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(comparisonData, null, 2)
    )}`;
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', jsonString);
    downloadAnchor.setAttribute('download', `ecoroute_${selectedScenarioId}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const activeResult =
    comparisonData && comparisonData.comparison_summary
      ? comparisonData.comparison_summary[activeAlgorithm]
      : null;

  const totalDemand = scenarioData?.collection_points?.reduce(
    (sum, p) => sum + p.waste_demand_kg,
    0
  ) || 0;

  return (
    <div className="app-wrapper">
      {/* Enterprise Header */}
      <header className="app-header">
        <div className="brand-section">
          <div className="brand-logo-badge">
            <Truck size={20} />
          </div>
          <div>
            <div className="brand-name">EcoRoute</div>
            <div className="brand-tagline">Municipal Solid Waste Collection Route Optimization</div>
          </div>
        </div>

        {/* Status & Actions */}
        <div className="header-meta">
          {scenarioData && (
            <div className="header-summary-badge">
              <MapPin size={15} color="var(--primary)" />
              <span>
                <strong>{scenarioData.collection_points.length} Collection Points</strong> •{' '}
                {Math.round(totalDemand).toLocaleString()} kg Total Waste
              </span>
            </div>
          )}

          <button
            className="btn btn-secondary"
            onClick={handleExportReport}
            disabled={!comparisonData}
          >
            <Download size={15} />
            <span>Export Route Plan</span>
          </button>

          <a
            href="https://github.com/Vineesh-12/EcoRoute"
            target="_blank"
            rel="noreferrer"
            className="btn btn-secondary"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
            <span>GitHub</span>
          </a>
        </div>
      </header>

      {/* Main Container */}
      <main className="layout-container">
        {/* Left Column: Simple Operational Controls */}
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
          activeAlgorithm={activeAlgorithm}
          onSelectAlgorithm={setActiveAlgorithm}
        />

        {/* Right Column: Clean Map & Comparison */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Map Card */}
          <div className="card">
            <div className="card-header">
              <div>
                <div className="card-title">Live Route Map</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Showing routes optimized using{' '}
                  <strong style={{ color: 'var(--primary)' }}>
                    {activeResult?.algorithm_name || 'Optimization Solver'}
                  </strong>
                </div>
              </div>

              {activeResult && (
                <div style={{ fontSize: '0.85rem', color: 'var(--text-main)', fontWeight: 600 }}>
                  Total Distance: <span style={{ color: 'var(--primary)' }}>{activeResult.total_distance_km} km</span> •{' '}
                  Travel Time: <span style={{ color: 'var(--primary)' }}>{activeResult.total_time_min} mins</span>
                </div>
              )}
            </div>

            <MapComponent
              depot={scenarioData?.depot}
              points={scenarioData?.collection_points}
              activeResult={activeResult}
              selectedVehicleIndex={selectedVehicleIndex}
              onSelectVehicle={setSelectedVehicleIndex}
            />
          </div>

          {/* Performance & Savings Metrics */}
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

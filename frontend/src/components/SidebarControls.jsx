import React from 'react';
import { Truck, MapPin, Play, RotateCw } from 'lucide-react';

const FLEET_COLORS = [
  '#1e40af', // Vehicle 1: Deep Blue
  '#059669', // Vehicle 2: Forest Emerald
  '#d97706', // Vehicle 3: Warm Amber
  '#7c3aed', // Vehicle 4: Purple
  '#0284c7', // Vehicle 5: Sky Blue
  '#dc2626', // Vehicle 6: Red
];

export default function SidebarControls({
  scenarios,
  selectedScenarioId,
  onSelectScenario,
  scenarioData,
  truckCount,
  setTruckCount,
  truckCapacity,
  setTruckCapacity,
  onRunOptimization,
  loading,
  activeResult,
  selectedVehicleIndex,
  onSelectVehicle,
}) {
  const points = scenarioData ? scenarioData.collection_points : [];
  const totalDemand = points.reduce((sum, p) => sum + p.waste_demand_kg, 0);
  const totalFleetCapacity = truckCount * truckCapacity;
  const isCapacityAdequate = totalFleetCapacity >= totalDemand;
  const routes = activeResult ? activeResult.routes : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* 1. Municipal Area Selection */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <MapPin size={16} color="var(--primary)" />
            <span>Select Municipal Area</span>
          </div>
        </div>

        <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <select
            id="scenario-selector"
            className="form-select"
            value={selectedScenarioId}
            onChange={(e) => onSelectScenario(e.target.value)}
            disabled={loading}
          >
            {scenarios.map((sc) => (
              <option key={sc.id} value={sc.id}>
                {sc.name}
              </option>
            ))}
          </select>

          {scenarioData && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '0.75rem',
                fontSize: '0.8rem',
              }}
            >
              <div
                style={{
                  background: 'var(--bg-subtle)',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-md)',
                }}
              >
                <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 600 }}>
                  COLLECTION BINS
                </div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, marginTop: '2px', color: 'var(--text-main)' }}>
                  {points.length} Locations
                </div>
              </div>

              <div
                style={{
                  background: 'var(--bg-subtle)',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-md)',
                }}
              >
                <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 600 }}>
                  ESTIMATED WASTE
                </div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, marginTop: '2px', color: 'var(--warning-text)' }}>
                  {Math.round(totalDemand).toLocaleString()} kg
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 2. Collection Truck Fleet Settings */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <Truck size={16} color="var(--primary)" />
            <span>Truck Fleet Settings</span>
          </div>
        </div>

        <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <div className="form-label">
              <span>Available Trucks</span>
              <strong>{truckCount} Trucks</strong>
            </div>
            <input
              id="truck-count-slider"
              type="range"
              min={2}
              max={6}
              value={truckCount}
              onChange={(e) => setTruckCount(parseInt(e.target.value))}
              disabled={loading}
              className="form-range"
            />
          </div>

          <div className="form-group">
            <div className="form-label">
              <span>Capacity per Truck</span>
              <strong>{truckCapacity} kg</strong>
            </div>
            <input
              id="truck-capacity-slider"
              type="range"
              min={300}
              max={1000}
              step={50}
              value={truckCapacity}
              onChange={(e) => setTruckCapacity(parseInt(e.target.value))}
              disabled={loading}
              className="form-range"
            />
          </div>

          <div
            style={{
              padding: '0.65rem 0.85rem',
              borderRadius: 'var(--radius-md)',
              background: isCapacityAdequate ? 'var(--success-light)' : 'var(--warning-light)',
              color: isCapacityAdequate ? 'var(--success-text)' : 'var(--warning-text)',
              fontSize: '0.78rem',
              fontWeight: 600,
            }}
          >
            {isCapacityAdequate
              ? `✓ Total fleet capacity (${totalFleetCapacity} kg) is sufficient`
              : `⚠ Fleet capacity (${totalFleetCapacity} kg) is less than waste (${Math.round(totalDemand)} kg)`}
          </div>

          <button
            id="run-optimization-btn"
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.75rem', marginTop: '0.25rem' }}
            onClick={onRunOptimization}
            disabled={loading}
          >
            {loading ? (
              <>
                <RotateCw className="animate-spin" size={16} />
                <span>Calculating Best Routes...</span>
              </>
            ) : (
              <>
                <Play size={16} />
                <span>Optimize Collection Routes</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* 3. Assigned Truck Routes Breakdown */}
      {routes.length > 0 && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <span>Assigned Truck Routes</span>
            </div>
            {selectedVehicleIndex !== null && (
              <button
                className="btn btn-secondary"
                style={{ padding: '0.25rem 0.6rem', fontSize: '0.72rem' }}
                onClick={() => onSelectVehicle(null)}
              >
                Show All
              </button>
            )}
          </div>

          <div className="card-body" style={{ padding: '0.85rem' }}>
            {routes.map((route, idx) => {
              const isSelected = selectedVehicleIndex === idx;
              const color = FLEET_COLORS[idx % FLEET_COLORS.length];
              const fillPct = route.capacity_utilization_pct;

              return (
                <div
                  key={idx}
                  className={`truck-route-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => onSelectVehicle(isSelected ? null : idx)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ width: 10, height: 10, borderRadius: '50%', background: color }} />
                      <strong style={{ fontSize: '0.88rem' }}>{route.vehicle_name}</strong>
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                      {route.total_distance_km} km
                    </span>
                  </div>

                  <div style={{ marginTop: '0.5rem' }}>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: '0.75rem',
                        color: 'var(--text-muted)',
                      }}
                    >
                      <span>
                        Waste Collected: {route.total_waste_collected_kg} / {route.capacity_kg} kg
                      </span>
                      <strong>{fillPct}% full</strong>
                    </div>

                    <div className="truck-progress-bar">
                      <div
                        className="truck-progress-fill"
                        style={{ width: `${fillPct}%`, background: color }}
                      />
                    </div>
                  </div>

                  <div style={{ fontSize: '0.74rem', color: 'var(--text-light)', marginTop: '0.45rem' }}>
                    Stops: {route.steps.filter((s) => s.step_type === 'collection').length} collection points •{' '}
                    {route.total_time_min} mins
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

import React from 'react';
import { Truck, Layers, Play, CheckCircle2, RotateCcw } from 'lucide-react';

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
    <div className="control-sidebar">
      {/* 1. Scenario Selection Panel */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <div className="section-title">
          <Layers size={18} color="#10b981" /> Municipal Scenario
        </div>
        <select
          id="scenario-selector"
          className="custom-select"
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
              marginTop: '0.85rem',
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '0.65rem',
              fontSize: '0.78rem',
            }}
          >
            <div
              style={{
                background: 'rgba(255,255,255,0.03)',
                padding: '0.5rem 0.65rem',
                borderRadius: '6px',
              }}
            >
              <div style={{ color: '#94a3b8' }}>Collection Points</div>
              <div style={{ fontSize: '1rem', fontWeight: '700' }}>
                {points.length} Bins
              </div>
            </div>
            <div
              style={{
                background: 'rgba(255,255,255,0.03)',
                padding: '0.5rem 0.65rem',
                borderRadius: '6px',
              }}
            >
              <div style={{ color: '#94a3b8' }}>Total Waste Demand</div>
              <div style={{ fontSize: '1rem', fontWeight: '700', color: '#f59e0b' }}>
                {Math.round(totalDemand)} kg
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 2. Vehicle Fleet Configuration */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <div className="section-title">
          <Truck size={18} color="#3b82f6" /> Collection Fleet Configuration
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          <div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '0.8rem',
                marginBottom: '0.35rem',
              }}
            >
              <span style={{ color: '#94a3b8' }}>Number of Vehicles:</span>
              <strong style={{ color: '#f8fafc' }}>{truckCount} Trucks</strong>
            </div>
            <input
              id="truck-count-slider"
              type="range"
              min={2}
              max={6}
              value={truckCount}
              onChange={(e) => setTruckCount(parseInt(e.target.value))}
              disabled={loading}
              style={{ width: '100%', accentColor: '#10b981', cursor: 'pointer' }}
            />
          </div>

          <div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '0.8rem',
                marginBottom: '0.35rem',
              }}
            >
              <span style={{ color: '#94a3b8' }}>Capacity per Vehicle:</span>
              <strong style={{ color: '#f8fafc' }}>{truckCapacity} kg</strong>
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
              style={{ width: '100%', accentColor: '#3b82f6', cursor: 'pointer' }}
            />
          </div>

          <div
            style={{
              fontSize: '0.74rem',
              padding: '0.5rem',
              borderRadius: '6px',
              background: isCapacityAdequate
                ? 'rgba(16, 185, 129, 0.1)'
                : 'rgba(244, 63, 94, 0.15)',
              color: isCapacityAdequate ? '#34d399' : '#fb7185',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <CheckCircle2 size={14} />
            <span>
              Total Fleet Capacity: <strong>{totalFleetCapacity} kg</strong>{' '}
              {isCapacityAdequate
                ? `(Surplus: +${totalFleetCapacity - Math.round(totalDemand)} kg)`
                : `(Deficit: -${Math.round(totalDemand) - totalFleetCapacity} kg)`}
            </span>
          </div>

          {/* Run Optimization Button */}
          <button
            id="run-optimization-btn"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '0.5rem', padding: '0.85rem' }}
            onClick={onRunOptimization}
            disabled={loading}
          >
            {loading ? (
              <>
                <RotateCcw className="animate-spin" size={16} /> Computing CVRP
                Routes...
              </>
            ) : (
              <>
                <Play size={16} /> Run Optimization & Compare
              </>
            )}
          </button>
        </div>
      </div>

      {/* 3. Vehicle Route Breakdown (When active result is loaded) */}
      {routes.length > 0 && (
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '0.85rem',
            }}
          >
            <div className="section-title" style={{ margin: 0 }}>
              <Truck size={18} color="#f59e0b" /> Assigned Vehicle Routes
            </div>
            {selectedVehicleIndex !== null && (
              <button
                className="btn btn-secondary"
                style={{ padding: '0.2rem 0.5rem', fontSize: '0.7rem' }}
                onClick={() => onSelectVehicle(null)}
              >
                Show All Routes
              </button>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {routes.map((route, idx) => {
              const isSelected = selectedVehicleIndex === idx;
              const fillPct = route.capacity_utilization_pct;
              const barColor =
                fillPct > 90 ? '#f43f5e' : fillPct > 70 ? '#f59e0b' : '#10b981';

              return (
                <div
                  key={idx}
                  onClick={() => onSelectVehicle(isSelected ? null : idx)}
                  style={{
                    padding: '0.75rem',
                    borderRadius: '8px',
                    background: isSelected
                      ? 'rgba(16, 185, 129, 0.15)'
                      : 'rgba(255,255,255,0.03)',
                    border: isSelected
                      ? '1px solid #10b981'
                      : '1px solid rgba(255,255,255,0.05)',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '0.82rem',
                    }}
                  >
                    <strong>{route.vehicle_name}</strong>
                    <span style={{ color: '#94a3b8' }}>
                      {route.total_distance_km} km • {route.total_time_min} min
                    </span>
                  </div>

                  <div className="utilization-bar-wrapper">
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: '0.72rem',
                        color: '#94a3b8',
                      }}
                    >
                      <span>
                        Load: {route.total_waste_collected_kg} / {route.capacity_kg} kg
                      </span>
                      <span style={{ color: barColor, fontWeight: '700' }}>
                        {fillPct}% Utilized
                      </span>
                    </div>
                    <div className="utilization-track">
                      <div
                        className="utilization-fill"
                        style={{ width: `${fillPct}%`, background: barColor }}
                      />
                    </div>
                  </div>

                  <div
                    style={{
                      marginTop: '0.45rem',
                      fontSize: '0.7rem',
                      color: '#64748b',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    Route: Depot →{' '}
                    {route.steps
                      .filter((s) => s.step_type === 'collection')
                      .map((s) => s.name.split(' ')[0])
                      .join(' → ')}{' '}
                    → Depot
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

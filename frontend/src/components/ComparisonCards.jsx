import React from 'react';
import { TrendingDown, Clock, Fuel, ShieldCheck, Zap } from 'lucide-react';

export default function ComparisonCards({
  comparisonData,
  activeAlgorithm,
  onSelectAlgorithm,
}) {
  if (!comparisonData || !comparisonData.comparison_summary) return null;

  const { comparison_summary, savings_vs_baseline, best_algorithm } = comparisonData;
  const bestResult = comparison_summary[best_algorithm];
  const bestSavings = savings_vs_baseline[best_algorithm] || {
    distance_saved_km: 0,
    distance_saved_pct: 0,
    time_saved_min: 0,
    time_saved_pct: 0,
    fuel_saved_liters: 0,
    co2_saved_kg: 0,
  };

  const algos = [
    { key: 'nearest_neighbor', label: 'Nearest Neighbor (Baseline)' },
    { key: 'genetic_algorithm', label: 'Genetic Algorithm (Metaheuristic)' },
    { key: 'ortools', label: 'Google OR-Tools (Benchmark Solver)' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Before vs After Impact Cards */}
      <div className="metrics-row">
        <div className="glass-panel metric-card green">
          <div className="metric-label">Distance Saved (vs Baseline)</div>
          <div className="metric-value">
            {bestSavings.distance_saved_km > 0
              ? `-${bestSavings.distance_saved_km} km`
              : 'Baseline'}
          </div>
          <div className="metric-badge badge-savings">
            <TrendingDown size={13} />
            {bestSavings.distance_saved_pct > 0
              ? `${bestSavings.distance_saved_pct}% Reduction`
              : 'Reference'}
          </div>
        </div>

        <div className="glass-panel metric-card blue">
          <div className="metric-label">Travel Time Saved</div>
          <div className="metric-value">
            {bestSavings.time_saved_min > 0
              ? `-${bestSavings.time_saved_min} min`
              : 'Baseline'}
          </div>
          <div className="metric-badge badge-savings">
            <Clock size={13} />
            {bestSavings.time_saved_pct > 0
              ? `${bestSavings.time_saved_pct}% Faster`
              : 'Reference'}
          </div>
        </div>

        <div className="glass-panel metric-card amber">
          <div className="metric-label">Fuel Consumption Saved</div>
          <div className="metric-value">
            {bestSavings.fuel_saved_liters > 0
              ? `${bestSavings.fuel_saved_liters} L`
              : '0.0 L'}
          </div>
          <div
            className="metric-badge"
            style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}
          >
            <Fuel size={13} /> Diesel Saved
          </div>
        </div>

        <div className="glass-panel metric-card rose">
          <div className="metric-label">CO2 Emissions Abated</div>
          <div className="metric-value">
            {bestSavings.co2_saved_kg > 0
              ? `${bestSavings.co2_saved_kg} kg`
              : '0.0 kg'}
          </div>
          <div
            className="metric-badge"
            style={{ background: 'rgba(244, 63, 94, 0.15)', color: '#fb7185' }}
          >
            <ShieldCheck size={13} /> Carbon Offset
          </div>
        </div>
      </div>

      {/* Head-to-Head Comparison Table */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '0.9rem',
          }}
        >
          <div className="section-title" style={{ margin: 0 }}>
            <Zap size={18} color="#10b981" /> Algorithm Performance Comparison
          </div>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            Click an algorithm row to view its routes on the map
          </span>
        </div>

        <div className="comparison-table-wrapper">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Algorithm</th>
                <th>Distance</th>
                <th>Travel Time</th>
                <th>Runtime</th>
                <th>Vehicles Used</th>
                <th>Violations</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {algos.map((item) => {
                const res = comparison_summary[item.key];
                if (!res) return null;
                const isBest = best_algorithm === item.key;
                const isSelected = activeAlgorithm === item.key;

                return (
                  <tr
                    key={item.key}
                    onClick={() => onSelectAlgorithm(item.key)}
                    style={{
                      cursor: 'pointer',
                      background: isSelected
                        ? 'rgba(16, 185, 129, 0.1)'
                        : 'transparent',
                    }}
                  >
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <strong
                          style={{
                            color: isSelected ? '#34d399' : '#f8fafc',
                          }}
                        >
                          {item.label}
                        </strong>
                        {isBest && <span className="best-pill">Best Solution</span>}
                      </div>
                    </td>
                    <td>
                      <span style={{ fontWeight: '700' }}>{res.total_distance_km} km</span>
                    </td>
                    <td>{res.total_time_min} mins</td>
                    <td>
                      <span style={{ color: '#94a3b8', fontFamily: 'monospace' }}>
                        {res.execution_time_ms} ms
                      </span>
                    </td>
                    <td>{res.vehicles_used} Trucks</td>
                    <td>
                      {res.capacity_violations === 0 ? (
                        <span style={{ color: '#34d399' }}>0 (Feasible)</span>
                      ) : (
                        <span style={{ color: '#f43f5e', fontWeight: 'bold' }}>
                          {res.capacity_violations} points dropped
                        </span>
                      )}
                    </td>
                    <td>
                      <button
                        className={`btn ${isSelected ? 'btn-active-algo' : 'btn-secondary'}`}
                        style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectAlgorithm(item.key);
                        }}
                      >
                        {isSelected ? 'Viewing' : 'Inspect'}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

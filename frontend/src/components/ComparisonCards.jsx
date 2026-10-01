import React from 'react';
import { TrendingDown, Clock, Fuel, Leaf, Check } from 'lucide-react';

export default function ComparisonCards({
  comparisonData,
  activeAlgorithm,
  onSelectAlgorithm,
}) {
  if (!comparisonData || !comparisonData.comparison_summary) return null;

  const { comparison_summary, savings_vs_baseline, best_algorithm } = comparisonData;
  const bestSavings = savings_vs_baseline[best_algorithm] || {
    distance_saved_km: 0,
    distance_saved_pct: 0,
    time_saved_min: 0,
    time_saved_pct: 0,
    fuel_saved_liters: 0,
    co2_saved_kg: 0,
  };

  const algos = [
    {
      key: 'ortools',
      name: 'Optimized Route Plan (OR-Tools)',
      desc: 'Industry standard optimization solver',
      tag: 'Best Result',
    },
    {
      key: 'genetic_algorithm',
      name: 'Smart Evolutionary Route (Genetic Algorithm)',
      desc: 'AI-inspired route permutation search',
      tag: null,
    },
    {
      key: 'nearest_neighbor',
      name: 'Standard Route (Nearest Neighbor)',
      desc: 'Unoptimized greedy baseline for reference',
      tag: 'Baseline',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* 1. Measurable Savings KPI Cards */}
      <div className="metrics-row">
        <div className="metric-box">
          <span className="metric-label">Distance Saved</span>
          <div className="metric-value" style={{ color: 'var(--success)' }}>
            {bestSavings.distance_saved_km > 0
              ? `-${bestSavings.distance_saved_km} km`
              : '0.0 km'}
          </div>
          <div className="metric-sub">
            <TrendingDown size={14} />
            <span>
              {bestSavings.distance_saved_pct > 0
                ? `${bestSavings.distance_saved_pct}% less travel`
                : 'Reference baseline'}
            </span>
          </div>
        </div>

        <div className="metric-box">
          <span className="metric-label">Travel Time Saved</span>
          <div className="metric-value" style={{ color: 'var(--primary)' }}>
            {bestSavings.time_saved_min > 0
              ? `-${bestSavings.time_saved_min} mins`
              : '0.0 mins'}
          </div>
          <div className="metric-sub" style={{ color: 'var(--primary)' }}>
            <Clock size={14} />
            <span>
              {bestSavings.time_saved_pct > 0
                ? `${bestSavings.time_saved_pct}% faster collection`
                : 'Reference baseline'}
            </span>
          </div>
        </div>

        <div className="metric-box">
          <span className="metric-label">Diesel Fuel Conserved</span>
          <div className="metric-value">
            {bestSavings.fuel_saved_liters > 0
              ? `${bestSavings.fuel_saved_liters} L`
              : '0.0 L'}
          </div>
          <div className="metric-sub" style={{ color: 'var(--warning)' }}>
            <Fuel size={14} />
            <span>Reduced fuel expense</span>
          </div>
        </div>

        <div className="metric-box">
          <span className="metric-label">CO2 Emissions Avoided</span>
          <div className="metric-value">
            {bestSavings.co2_saved_kg > 0
              ? `${bestSavings.co2_saved_kg} kg`
              : '0.0 kg'}
          </div>
          <div className="metric-sub">
            <Leaf size={14} />
            <span>Lower carbon footprint</span>
          </div>
        </div>
      </div>

      {/* 2. Route Comparison Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Route Optimization Comparison</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Comparison of route efficiency against traditional unoptimized routing
            </div>
          </div>
        </div>

        <div className="data-table-container">
          <table className="clean-table">
            <thead>
              <tr>
                <th>Routing Method</th>
                <th>Total Distance</th>
                <th>Distance Reduction</th>
                <th>Estimated Time</th>
                <th>Trucks Used</th>
                <th>Feasibility</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {algos.map((item) => {
                const res = comparison_summary[item.key];
                if (!res) return null;
                const isSelected = activeAlgorithm === item.key;
                const savings = savings_vs_baseline[item.key];

                return (
                  <tr
                    key={item.key}
                    className={isSelected ? 'active-row' : ''}
                    onClick={() => onSelectAlgorithm(item.key)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <strong style={{ color: 'var(--text-main)' }}>{item.name}</strong>
                          {item.tag && (
                            <span
                              style={{
                                fontSize: '0.7rem',
                                fontWeight: 700,
                                padding: '0.15rem 0.45rem',
                                borderRadius: 'var(--radius-sm)',
                                background:
                                  item.tag === 'Best Result'
                                    ? 'var(--success-light)'
                                    : 'var(--bg-subtle)',
                                color:
                                  item.tag === 'Best Result'
                                    ? 'var(--success-text)'
                                    : 'var(--text-muted)',
                              }}
                            >
                              {item.tag}
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-light)', marginTop: '2px' }}>
                          {item.desc}
                        </div>
                      </div>
                    </td>

                    <td>
                      <strong style={{ fontSize: '0.92rem', color: 'var(--text-main)' }}>
                        {res.total_distance_km} km
                      </strong>
                    </td>

                    <td>
                      {savings && savings.distance_saved_pct > 0 ? (
                        <span style={{ color: 'var(--success)', fontWeight: 700 }}>
                          -{savings.distance_saved_pct}% ({savings.distance_saved_km} km saved)
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)' }}>Baseline</span>
                      )}
                    </td>

                    <td>
                      <span>{res.total_time_min} mins</span>
                    </td>

                    <td>{res.vehicles_used} Trucks</td>

                    <td>
                      {res.capacity_violations === 0 ? (
                        <span style={{ color: 'var(--success)', fontWeight: 600, fontSize: '0.8rem' }}>
                          ✓ All bins collected
                        </span>
                      ) : (
                        <span style={{ color: '#ef4444', fontWeight: 600 }}>
                          {res.capacity_violations} bins unserved
                        </span>
                      )}
                    </td>

                    <td>
                      <button
                        className={`btn ${isSelected ? 'btn-primary' : 'btn-secondary'}`}
                        style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectAlgorithm(item.key);
                        }}
                      >
                        {isSelected ? 'Active' : 'View Route'}
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

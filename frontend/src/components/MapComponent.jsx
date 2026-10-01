import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';

// Professional fleet route colors
const FLEET_COLORS = [
  '#1e40af', // Vehicle 1: Deep Blue
  '#059669', // Vehicle 2: Forest Emerald
  '#d97706', // Vehicle 3: Warm Amber
  '#7c3aed', // Vehicle 4: Purple
  '#0284c7', // Vehicle 5: Sky Blue
  '#dc2626', // Vehicle 6: Red
];

// Helper to auto-fit map viewport bounds
function MapViewportController({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.length > 0) {
      map.fitBounds(bounds, { padding: [35, 35], maxZoom: 14 });
    }
  }, [bounds, map]);
  return null;
}

// Clean Enterprise Pin for Central Depot
const createDepotMarker = (name) => {
  return L.divIcon({
    className: 'leaflet-depot-pin',
    html: `
      <div style="
        background: #0f172a;
        border: 2px solid #ffffff;
        border-radius: 6px;
        padding: 4px 8px;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        font-weight: 700;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        gap: 5px;
        white-space: nowrap;
      ">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 21h18"/>
          <path d="M5 21V7l8-4v18"/>
          <path d="M19 21V11l-6-3"/>
        </svg>
        <span>DEPOT</span>
      </div>
    `,
    iconSize: [72, 28],
    iconAnchor: [36, 14],
    popupAnchor: [0, -15],
  });
};

// Clean Enterprise Pin for Collection Bins
const createCollectionPin = (id, demandKg) => {
  return L.divIcon({
    className: 'leaflet-bin-pin',
    html: `
      <div style="
        background: #ffffff;
        border: 1.5px solid #0f172a;
        border-radius: 4px;
        padding: 2px 6px;
        font-family: 'Inter', sans-serif;
        font-size: 10px;
        font-weight: 700;
        color: #0f172a;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 3px;
        white-space: nowrap;
      ">
        <span style="color: #2563eb">#${id}</span>
        <span style="color: #cbd5e1">|</span>
        <span>${Math.round(demandKg)}kg</span>
      </div>
    `,
    iconSize: [58, 22],
    iconAnchor: [29, 11],
    popupAnchor: [0, -12],
  });
};

export default function MapComponent({
  depot,
  points,
  activeResult,
  selectedVehicleIndex,
  onSelectVehicle,
}) {
  if (!depot) return null;

  // Compute map bounds covering depot and collection points
  const allCoords = [[depot.latitude, depot.longitude]];
  if (points) {
    points.forEach((p) => allCoords.push([p.latitude, p.longitude]));
  }

  const routes = activeResult ? activeResult.routes : [];

  return (
    <div style={{ position: 'relative' }}>
      {/* Route Filter Ribbon */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.65rem 1.25rem',
          background: '#f8fafc',
          borderBottom: '1px solid var(--border-default)',
          fontSize: '0.8rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Filter by Vehicle:</span>
          <button
            className={`btn ${selectedVehicleIndex === null ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.25rem 0.65rem', fontSize: '0.75rem' }}
            onClick={() => onSelectVehicle(null)}
          >
            All Trucks ({routes.length})
          </button>

          {routes.map((r, idx) => {
            const isSelected = selectedVehicleIndex === idx;
            const color = FLEET_COLORS[idx % FLEET_COLORS.length];
            return (
              <button
                key={idx}
                className="btn btn-secondary"
                style={{
                  padding: '0.25rem 0.65rem',
                  fontSize: '0.75rem',
                  border: isSelected ? `2px solid ${color}` : '1px solid var(--border-strong)',
                  background: isSelected ? 'var(--primary-light)' : '#ffffff',
                  fontWeight: isSelected ? 700 : 500,
                }}
                onClick={() => onSelectVehicle(isSelected ? null : idx)}
              >
                <span
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: color,
                    display: 'inline-block',
                  }}
                />
                <span>Truck {idx + 1}</span>
              </button>
            );
          })}
        </div>

        <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 500 }}>
          {points ? `${points.length} Collection Locations` : ''}
        </div>
      </div>

      {/* Map Canvas */}
      <MapContainer
        center={[depot.latitude, depot.longitude]}
        zoom={12}
        scrollWheelZoom={true}
        className="map-frame"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapViewportController bounds={allCoords} />

        {/* Central Municipal Depot Marker */}
        <Marker
          position={[depot.latitude, depot.longitude]}
          icon={createDepotMarker(depot.name)}
        >
          <Popup>
            <div style={{ padding: '4px', color: '#0f172a', fontFamily: 'Inter, sans-serif' }}>
              <div style={{ fontSize: '11px', color: '#2563eb', fontWeight: 700, textTransform: 'uppercase' }}>
                Municipal Depot (Start & Finish)
              </div>
              <div style={{ fontWeight: 700, fontSize: '13px', marginTop: '2px' }}>{depot.name}</div>
              <div style={{ fontSize: '11px', color: '#64748b', marginTop: '3px' }}>
                {depot.address || 'Central Fleet Dispatch and Landfill Facility'}
              </div>
            </div>
          </Popup>
        </Marker>

        {/* Collection Point Bins */}
        {points &&
          points.map((p) => (
            <Marker
              key={p.id}
              position={[p.latitude, p.longitude]}
              icon={createCollectionPin(p.id, p.waste_demand_kg)}
            >
              <Popup>
                <div style={{ padding: '4px', color: '#0f172a', fontFamily: 'Inter, sans-serif', minWidth: '160px' }}>
                  <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
                    Bin Station #{p.id}
                  </div>
                  <div style={{ fontWeight: 700, fontSize: '13px', marginTop: '2px' }}>{p.name}</div>
                  <div style={{ marginTop: '6px', fontSize: '12px', display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#64748b' }}>Estimated Waste:</span>
                    <strong style={{ color: '#0f172a' }}>{p.waste_demand_kg} kg</strong>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}

        {/* Polylines for Assigned Vehicle Routes */}
        {routes.map((route, idx) => {
          if (selectedVehicleIndex !== null && selectedVehicleIndex !== idx) {
            return null;
          }

          const color = FLEET_COLORS[idx % FLEET_COLORS.length];
          const path = route.path_coordinates || [];

          return (
            <Polyline
              key={`route-line-${route.vehicle_id}-${idx}`}
              positions={path}
              pathOptions={{
                color: color,
                weight: 4.5,
                opacity: 0.9,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            >
              <Popup>
                <div style={{ padding: '4px', color: '#0f172a', fontFamily: 'Inter, sans-serif' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: color }} />
                    <strong style={{ fontSize: '13px' }}>{route.vehicle_name}</strong>
                  </div>
                  <div style={{ marginTop: '8px', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '3px' }}>
                    <div>Distance: <strong>{route.total_distance_km} km</strong></div>
                    <div>Travel Time: <strong>{route.total_time_min} mins</strong></div>
                    <div>Waste Collected: <strong>{route.total_waste_collected_kg} / {route.capacity_kg} kg ({route.capacity_utilization_pct}%)</strong></div>
                    <div>Stops: <strong>{route.steps.length - 2} collection points</strong></div>
                  </div>
                </div>
              </Popup>
            </Polyline>
          );
        })}
      </MapContainer>
    </div>
  );
}

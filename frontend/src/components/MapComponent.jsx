import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';

// Fix Leaflet's default icon path issues in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Color palette for distinct vehicle routes
const ROUTE_COLORS = [
  '#10b981', // Emerald
  '#3b82f6', // Blue
  '#f59e0b', // Amber
  '#ec4899', // Pink
  '#8b5cf6', // Purple
  '#06b6d4', // Cyan
];

// Helper component to auto-recenter map bounds
function AutoRecenter({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.length > 0) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
    }
  }, [bounds, map]);
  return null;
}

// Custom SVG Icons
const createDepotIcon = () => {
  return L.divIcon({
    className: 'custom-depot-pin',
    html: `
      <div style="
        background: #10b981;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid white;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.8);
        color: white;
        font-weight: 800;
        font-size: 14px;
      ">
        🏢
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
  });
};

const createPointIcon = (demand) => {
  const isHigh = demand > 120;
  const bgColor = isHigh ? '#f43f5e' : demand > 80 ? '#f59e0b' : '#3b82f6';
  return L.divIcon({
    className: 'custom-bin-pin',
    html: `
      <div style="
        background: ${bgColor};
        color: white;
        padding: 2px 6px;
        border-radius: 12px;
        border: 1.5px solid white;
        font-size: 11px;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 3px;
      ">
        <span>🗑️</span> ${Math.round(demand)}kg
      </div>
    `,
    iconSize: [50, 24],
    iconAnchor: [25, 12],
    popupAnchor: [0, -12]
  });
};

export default function MapComponent({ depot, points, activeResult, selectedVehicleIndex }) {
  if (!depot) return null;

  // Compute map bounds covering depot and all collection points
  const allCoords = [[depot.latitude, depot.longitude]];
  if (points) {
    points.forEach((p) => allCoords.push([p.latitude, p.longitude]));
  }

  const routes = activeResult ? activeResult.routes : [];

  return (
    <div className="map-view-wrapper">
      <MapContainer
        center={[depot.latitude, depot.longitude]}
        zoom={12}
        scrollWheelZoom={true}
        className="leaflet-container"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <AutoRecenter bounds={allCoords} />

        {/* Depot Marker */}
        <Marker
          position={[depot.latitude, depot.longitude]}
          icon={createDepotIcon()}
        >
          <Popup>
            <div style={{ color: '#0f172a', fontWeight: 'bold' }}>
              <div style={{ color: '#059669', fontSize: '13px' }}>🏢 Central Municipal Depot</div>
              <div>{depot.name}</div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>{depot.address || 'Starting & Ending point'}</div>
            </div>
          </Popup>
        </Marker>

        {/* Collection Points Markers */}
        {points &&
          points.map((p) => (
            <Marker
              key={p.id}
              position={[p.latitude, p.longitude]}
              icon={createPointIcon(p.waste_demand_kg)}
            >
              <Popup>
                <div style={{ color: '#0f172a', minWidth: '150px' }}>
                  <div style={{ fontWeight: '700', fontSize: '13px' }}>{p.name}</div>
                  <div style={{ margin: '4px 0', fontSize: '12px' }}>
                    <strong>Waste Quantity:</strong>{' '}
                    <span style={{ color: '#f43f5e', fontWeight: '700' }}>
                      {p.waste_demand_kg} kg
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>
                    Estimated Service Time: {p.service_time_min} mins
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}

        {/* Render Vehicle Routes Polylines */}
        {routes.map((route, idx) => {
          if (
            selectedVehicleIndex !== null &&
            selectedVehicleIndex !== undefined &&
            selectedVehicleIndex !== idx
          ) {
            return null; // Filter to selected vehicle if requested
          }

          const color = ROUTE_COLORS[idx % ROUTE_COLORS.length];
          const path = route.path_coordinates || [];

          return (
            <React.Fragment key={`route-${route.vehicle_id}-${idx}`}>
              <Polyline
                positions={path}
                pathOptions={{
                  color: color,
                  weight: 5,
                  opacity: 0.85,
                  lineJoin: 'round',
                }}
              >
                <Popup>
                  <div style={{ color: '#0f172a' }}>
                    <strong style={{ color: color, fontSize: '13px' }}>
                      🚛 {route.vehicle_name}
                    </strong>
                    <div style={{ fontSize: '12px', marginTop: '4px' }}>
                      <div>
                        <strong>Distance:</strong> {route.total_distance_km} km
                      </div>
                      <div>
                        <strong>Travel Time:</strong> {route.total_time_min} mins
                      </div>
                      <div>
                        <strong>Waste Load:</strong> {route.total_waste_collected_kg} /{' '}
                        {route.capacity_kg} kg ({route.capacity_utilization_pct}%)
                      </div>
                      <div>
                        <strong>Stops:</strong> {route.steps.length - 2} collection points
                      </div>
                    </div>
                  </div>
                </Popup>
              </Polyline>
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
}

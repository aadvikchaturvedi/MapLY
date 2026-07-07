"use client";

import { useEffect, useRef } from "react";
import { MapContainer as LeafletMap, TileLayer, Polyline, Circle, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-routing-machine/dist/leaflet-routing-machine.css";
import type { UserLocation } from "@/types";

const DEFAULT_CENTER: [number, number] = [28.61, 77.23];
const DEFAULT_ZOOM = 12;

const RISK_PALETTE: Record<string, string> = {
  "Low Risk": "#10B981",
  "Moderate Risk": "#F59E0B",
  "High Risk": "#EF4444",
};

function getColorForScore(score: number): string {
  if (score < 0.3) return "#10B981";
  if (score <= 0.6) return "#F59E0B";
  return "#EF4444";
}

const userIcon = L.divIcon({
  className: "",
  html: `<div style="width:16px;height:16px;background:#3B82F6;border:3px solid white;border-radius:50%;box-shadow:0 0 20px rgba(59,130,246,0.6)"></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8],
});

const destIcon = L.divIcon({
  className: "",
  html: `<div style="width:24px;height:24px;background:#EF4444;border:3px solid white;border-radius:50%;box-shadow:0 0 20px rgba(239,68,68,0.6);display:flex;align-items:center;justify-content:center"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><circle cx="12" cy="12" r="10"/></svg></div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

function MapBoundsUpdater({ segments }: { segments: Array<{ risk: string; risk_score: number; path: Array<[number, number]> }> }) {
  const map = useMap();
  const initialized = useRef(false);

  useEffect(() => {
    if (!segments || segments.length === 0 || initialized.current) return;
    const allPoints: [number, number][] = [];
    for (const seg of segments) {
      for (const pt of seg.path) {
        if (pt && pt.length === 2) allPoints.push(pt);
      }
    }
    if (allPoints.length > 0) {
      try {
        const bounds = L.latLngBounds(allPoints);
        map.fitBounds(bounds, { padding: [50, 50] });
        initialized.current = true;
      } catch {
        // ignore bounds fitting errors
      }
    }
  }, [segments, map]);

  return null;
}

interface MapProps {
  segments?: Array<{ risk: string; risk_score: number; path: Array<[number, number]> }>;
  userLocation?: UserLocation | null;
  destination?: { lat: number; lng: number } | null;
}

export default function Map({
  segments = [],
  userLocation = null,
  destination = null,
}: MapProps) {
  const center: [number, number] = userLocation
    ? [userLocation.lat, userLocation.lng]
    : DEFAULT_CENTER;

  return (
    <LeafletMap
      center={center}
      zoom={DEFAULT_ZOOM}
      style={{ height: "100%", width: "100%" }}
      zoomControl={false}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />

      {userLocation && (
        <>
          <Marker position={[userLocation.lat, userLocation.lng]} icon={userIcon}>
            <Popup>You are here</Popup>
          </Marker>
          <Circle
            center={[userLocation.lat, userLocation.lng]}
            radius={userLocation.accuracy ?? 50}
            pathOptions={{
              color: "#3B82F6",
              fillColor: "#3B82F6",
              fillOpacity: 0.1,
              weight: 1,
            }}
          />
        </>
      )}

      {destination && (
        <Marker position={[destination.lat, destination.lng]} icon={destIcon}>
          <Popup>Destination</Popup>
        </Marker>
      )}

      {segments.map((seg, idx) => {
        const color = seg.risk_score !== undefined
          ? getColorForScore(seg.risk_score)
          : RISK_PALETTE[seg.risk] ?? "#10B981";
        return (
          <Polyline
            key={idx}
            positions={seg.path}
            pathOptions={{ color, weight: 5, opacity: 0.85 }}
          />
        );
      })}

      <MapBoundsUpdater segments={segments} />
    </LeafletMap>
  );
}

"use client";

import { useEffect, useMemo } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import type { RouteSegment } from "@/types";

const HEAT_COLORS = [
  { threshold: 0.0, color: "rgba(16, 185, 129, 0.12)" },
  { threshold: 0.3, color: "rgba(245, 158, 11, 0.12)" },
  { threshold: 0.6, color: "rgba(239, 68, 68, 0.18)" },
];

interface HeatmapProps {
  segments: RouteSegment[];
  visible?: boolean;
}

function findColor(score: number): string {
  for (let i = HEAT_COLORS.length - 1; i >= 0; i--) {
    if (score >= HEAT_COLORS[i].threshold) return HEAT_COLORS[i].color;
  }
  return HEAT_COLORS[0].color;
}

export default function Heatmap({ segments, visible = true }: HeatmapProps) {
  const map = useMap();

  const heatPoints = useMemo(() => {
    if (!segments || segments.length === 0 || !visible) return [];

    const step = Math.max(1, Math.floor(segments.length / 50));
    const points: Array<{ lat: number; lng: number; radius: number; color: string }> = [];

    for (let i = 0; i < segments.length; i += step) {
      const seg = segments[i];
      points.push({
        lat: seg.lat,
        lng: seg.lng,
        radius: 120 + seg.risk_score * 180,
        color: findColor(seg.risk_score),
      });
    }

    return points;
  }, [segments, visible]);

  useEffect(() => {
    if (!map || heatPoints.length === 0 || !visible) return;

    const bounds = map.getBounds();
    const canvas = document.createElement("canvas");
    const size = map.getSize();
    canvas.width = size.x;
    canvas.height = size.y;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    for (const pt of heatPoints) {
      if (!bounds.contains([pt.lat, pt.lng])) continue;
      const point = map.latLngToContainerPoint([pt.lat, pt.lng]);
      const gradient = ctx.createRadialGradient(point.x, point.y, 0, point.x, point.y, pt.radius);
      gradient.addColorStop(0, pt.color);
      gradient.addColorStop(1, "transparent");
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(point.x, point.y, pt.radius, 0, Math.PI * 2);
      ctx.fill();
    }

    const overlay = L.imageOverlay(canvas.toDataURL(), bounds);
    overlay.addTo(map);

    return () => {
      overlay.remove();
    };
  }, [map, heatPoints, visible]);

  return null;
}

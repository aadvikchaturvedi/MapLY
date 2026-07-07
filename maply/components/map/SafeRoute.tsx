"use client";

import { useMemo } from "react";
import { Polyline, useMap } from "react-leaflet";
import type { RouteSegment } from "@/types";

const RISK_TO_COLOR: Record<string, string> = {
  low: "#10B981",
  moderate: "#F59E0B",
  high: "#EF4444",
};

function toColor(riskScore: number): string {
  if (riskScore < 0.3) return "#10B981";
  if (riskScore <= 0.6) return "#F59E0B";
  return "#EF4444";
}

interface SafeRouteProps {
  segments: RouteSegment[];
}

export default function SafeRoute({ segments }: SafeRouteProps) {
  const map = useMap();

  const polylines = useMemo(() => {
    if (!segments || segments.length < 2) return [];

    const lines: Array<{ positions: Array<[number, number]>; color: string; key: string }> = [];

    for (let i = 0; i < segments.length - 1; i++) {
      const curr = segments[i];
      const next = segments[i + 1];
      const color = toColor(curr.risk_score);

      const last = lines[lines.length - 1];
      if (last && last.color === color) {
        last.positions.push([next.lat, next.lng]);
      } else {
        lines.push({
          positions: [
            [curr.lat, curr.lng],
            [next.lat, next.lng],
          ],
          color,
          key: `seg-${i}`,
        });
      }
    }

    return lines;
  }, [segments]);

  if (!segments || segments.length < 2) return null;

  return (
    <>
      {polylines.map((line) => (
        <Polyline
          key={line.key}
          positions={line.positions}
          pathOptions={{
            color: line.color,
            weight: 5,
            opacity: 0.85,
          }}
        />
      ))}
    </>
  );
}

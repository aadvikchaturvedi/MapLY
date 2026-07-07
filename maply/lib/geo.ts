/**
 * Geospatial helpers used across the navigation stack.
 *
 * - `haversine`     : great-circle distance between two LatLng points.
 * - `interpolateRoute` : densify a sparse coordinate sequence so the
 *   polyline never has consecutive points farther than `maxSpacingMeters`
 *   apart. Used before sending a route to the risk-scoring backend.
 * - `chunkPolyline` : split a polyline into fixed-length chunks of
 *   approximately `chunkSizeMeters`. Useful for batching risk-score
 *   requests and for animated drawing.
 */

import type { LatLng } from "@/types";

/** Mean Earth radius in metres (WGS-84 spherical approximation). */
const EARTH_RADIUS_METERS = 6_371_008.8;

/** Convert degrees to radians. */
function toRadians(degrees: number): number {
  return (degrees * Math.PI) / 180;
}

/**
 * Great-circle distance between two LatLng points, in metres, using
 * the haversine formula. Safe for any pair of valid coordinates; both
 * inputs are clamped to their legal ranges to avoid NaN from cosines
 * at the poles / antimeridian.
 */
export function haversine(a: LatLng, b: LatLng): number {
  if (
    !Number.isFinite(a.lat) ||
    !Number.isFinite(a.lng) ||
    !Number.isFinite(b.lat) ||
    !Number.isFinite(b.lng)
  ) {
    return NaN;
  }

  const lat1 = Math.max(-90, Math.min(90, a.lat));
  const lat2 = Math.max(-90, Math.min(90, b.lat));
  const dLat = toRadians(lat2 - lat1);
  const dLng = toRadians(b.lng - a.lng);

  const sinDLat = Math.sin(dLat / 2);
  const sinDLng = Math.sin(dLng / 2);

  const h =
    sinDLat * sinDLat +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      sinDLng *
      sinDLng;

  const c = 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
  return EARTH_RADIUS_METERS * c;
}

/**
 * Densify a coordinate sequence so consecutive points are at most
 * `maxSpacingMeters` apart. Linear interpolation is performed in
 * (lat, lng) space, which is acceptable for the short segments
 * produced here (<= 200 m by default) and avoids the complexity of
 * great-circle interpolation.
 *
 * - Returns an empty array when given an empty input.
 * - Returns the original sequence unchanged when it contains a
 *   single point.
 * - Skips non-finite points silently to keep downstream rendering
 *   robust against bad geocoder responses.
 */
export function interpolateRoute(
  coordinates: LatLng[],
  maxSpacingMeters: number = 200
): LatLng[] {
  if (!Array.isArray(coordinates) || coordinates.length === 0) return [];
  if (coordinates.length === 1) return [{ ...coordinates[0] }];

  const spacing = Math.max(1, maxSpacingMeters);
  const result: LatLng[] = [];

  for (let i = 0; i < coordinates.length - 1; i++) {
    const start = coordinates[i];
    const end = coordinates[i + 1];

    if (
      !Number.isFinite(start.lat) ||
      !Number.isFinite(start.lng) ||
      !Number.isFinite(end.lat) ||
      !Number.isFinite(end.lng)
    ) {
      // Push whichever side is finite so the caller still gets a
      // usable (if shorter) sequence.
      if (Number.isFinite(start.lat) && Number.isFinite(start.lng)) {
        result.push({ lat: start.lat, lng: start.lng });
      }
      continue;
    }

    result.push({ lat: start.lat, lng: start.lng });

    const segmentLength = haversine(start, end);
    if (!Number.isFinite(segmentLength) || segmentLength <= spacing) {
      continue;
    }

    const steps = Math.ceil(segmentLength / spacing);
    for (let step = 1; step < steps; step++) {
      const t = step / steps;
      result.push({
        lat: start.lat + (end.lat - start.lat) * t,
        lng: start.lng + (end.lng - start.lng) * t,
      });
    }
  }

  const last = coordinates[coordinates.length - 1];
  if (Number.isFinite(last.lat) && Number.isFinite(last.lng)) {
    result.push({ lat: last.lat, lng: last.lng });
  }

  return result;
}

/**
 * Split a polyline into chunks of approximately `chunkSizeMeters`
 * total length. Each chunk is an array of `LatLng` points sharing the
 * joining endpoints with its neighbours. The final chunk may be
 * shorter than `chunkSizeMeters`.
 *
 * The first chunk always contains at least the first point; the
 * last chunk always contains the last point. Returns an empty
 * array for empty input.
 */
export function chunkPolyline(
  path: LatLng[],
  chunkSizeMeters: number = 200
): LatLng[][] {
  if (!Array.isArray(path) || path.length === 0) return [];
  if (path.length === 1) return [[{ ...path[0] }]];

  const chunkSize = Math.max(1, chunkSizeMeters);
  const chunks: LatLng[][] = [];
  let current: LatLng[] = [];
  let carriedDistance = 0;

  for (let i = 0; i < path.length; i++) {
    const point = path[i];
    if (!Number.isFinite(point.lat) || !Number.isFinite(point.lng)) continue;

    if (current.length === 0) {
      current.push({ lat: point.lat, lng: point.lng });
      continue;
    }

    const prev = current[current.length - 1];
    const segmentLength = haversine(prev, point);
    if (!Number.isFinite(segmentLength)) {
      // Skip the bad segment but keep the point so subsequent chunks
      // resume from a valid coordinate.
      current.push({ lat: point.lat, lng: point.lng });
      continue;
    }

    if (carriedDistance + segmentLength >= chunkSize && current.length >= 1) {
      // Close out the current chunk. The boundary point belongs to both
      // the previous and the next chunk so neighbouring chunks connect.
      chunks.push(current);
      current = [{ lat: point.lat, lng: point.lng }];
      carriedDistance = 0;
    } else {
      current.push({ lat: point.lat, lng: point.lng });
      carriedDistance += segmentLength;
    }
  }

  if (current.length > 0) chunks.push(current);
  return chunks;
}

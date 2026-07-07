/**
 * OSRM routing integration.
 *
 * Fetches driving routes from the public OSRM demo service and
 * returns a simplified array of [lat, lng] coordinates suitable
 * for risk scoring and Leaflet polyline rendering.
 */

const OSRM_BASE = "https://router.project-osrm.org/route/v1/driving";
const REQUEST_TIMEOUT_MS = 15_000;
const OSRM_HEADERS = {
  "User-Agent": "MapLY-Safety-Application/1.0",
};

/**
 * Fetch a driving route between two points from the OSRM public API.
 *
 * @param {{ lat: number, lng: number }} start
 * @param {{ lat: number, lng: number }} end
 * @returns {Promise<Array<[number, number]>>} Array of [lat, lng] coordinates
 */
export async function getRoute(start, end) {
  if (!start || !end) {
    throw new Error("start and end coordinates are required");
  }
  if (
    typeof start.lat !== "number" ||
    typeof start.lng !== "number" ||
    typeof end.lat !== "number" ||
    typeof end.lng !== "number"
  ) {
    throw new Error("start and end must have numeric lat/lng properties");
  }

  const url =
    `${OSRM_BASE}/${start.lng},${start.lat};${end.lng},${end.lat}` +
    `?overview=full&geometries=geojson&alternatives=false&steps=false`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  let response;
  try {
    response = await fetch(url, { signal: controller.signal, headers: OSRM_HEADERS });
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    throw new Error(
      `OSRM routing failed: ${response.status} ${response.statusText}`
    );
  }

  const data = await response.json();

  if (
    !data ||
    !data.routes ||
    data.routes.length === 0 ||
    !data.routes[0].geometry ||
    !data.routes[0].geometry.coordinates
  ) {
    throw new Error("OSRM returned an empty route");
  }

  // OSRM returns [lng, lat] — swap to [lat, lng]
  return data.routes[0].geometry.coordinates.map(([lng, lat]) => [lat, lng]);
}

/**
 * Simplify a route by taking every Nth point.
 * Helps reduce payload size before risk scoring.
 *
 * @param {Array<[number, number]>} coords - Array of [lat, lng]
 * @param {number} [every=10] - Take every Nth point
 * @returns {Array<[number, number]>}
 */
export function simplifyRoute(coords, every = 10) {
  if (!Array.isArray(coords) || coords.length === 0) return [];
  const step = Math.max(1, Math.floor(every));
  return coords.filter((_, i) => i % step === 0);
}

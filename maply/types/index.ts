/**
 * Shared TypeScript types for the MapLY navigation & risk system.
 *
 * These types are imported across hooks, components, and the Zustand store
 * so the frontend can speak a single vocabulary with the FastAPI backend.
 */

/** Latitude / longitude pair. `lat` in [-90, 90], `lng` in [-180, 180]. */
export interface LatLng {
  lat: number;
  lng: number;
}

/**
 * A single sampled point along a route with an attached risk evaluation.
 * Mirrors the response schema of `POST /api/v1/risk/route` on the FastAPI
 * backend (see Chunk 7 of the integration plan).
 */
export interface RouteSegment {
  lat: number;
  lng: number;
  /** Continuous risk score in [0, 1]; higher = riskier. */
  risk_score: number;
  /** Categorical bucket derived from `risk_score`. */
  risk_category: RiskTier;
}

/**
 * Coarse risk tier used for colouring map polylines and rendering the
 * legend. The thresholds match those used in `SafeRoute.tsx`.
 *  - `low`      : risk_score < 0.3
 *  - `moderate` : 0.3 <= risk_score <= 0.6
 *  - `high`     : risk_score > 0.6
 */
export type RiskTier = "low" | "moderate" | "high";

/** Payload sent to the backend (HTTP fallback or WebSocket) when the
 *  user triggers an SOS. */
export interface SOSPayload {
  lat: number;
  lng: number;
  /** Unix epoch milliseconds when the payload was produced. */
  timestamp: number;
  /** Mock JWT used to authenticate with the FastAPI service. */
  token: string;
  /** Optional identifier for the user/contact channel. */
  user_id?: string;
  /** Optional free-form note from the user. */
  note?: string;
}

/**
 * Authorization headers attached to every outbound request from the
 * web client. The values are mocked for now; production will swap in
 * a real session token.
 */
export interface AuthHeaders {
  Authorization: string;
  "x-maply-client": string;
}

/**
 * Lifecycle states for the SOS WebSocket connection. The store stores
 * this verbatim in `activeWebSocketStatus`.
 */
export type WebSocketStatus =
  | "idle"
  | "connecting"
  | "open"
  | "closed"
  | "error";

/**
 * A location chosen by the user as the navigation destination, either
 * via the floating search bar or by tapping the map.
 */
export interface DestinationLocation extends LatLng {
  /** Human-readable place name (e.g. "Connaught Place, New Delhi"). */
  name: string;
  /** Optional full address as returned by the geocoder. */
  address?: string;
}

/**
 * The user's current geolocation, optionally enriched with the
 * `GeolocationPosition` metadata from the browser API.
 */
export interface UserLocation extends LatLng {
  /** Horizontal accuracy in metres. */
  accuracy?: number;
  /** Heading in degrees, if available. */
  heading?: number;
  /** Ground speed in metres/second, if available. */
  speed?: number;
  /** Unix epoch milliseconds at which the position was sampled. */
  timestamp?: number;
}

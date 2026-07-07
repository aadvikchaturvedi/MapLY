# MapLY Navigation & State Integration Plan

## Objective
Replace placeholder scaffolds with a production-ready Google Maps-style risk-aware navigation system spanning Next.js frontend, FastAPI backend, and ML layer while preserving existing UI aesthetics and XGBoost risk model.

## Current State
- `maply/store/useStore.tsx` — empty file
- `maply/hooks/useLocation.ts` — empty file
- `maply/hooks/useSOS.ts` — empty file
- `maply/app/api/sos/route.ts` — empty file
- `maply/app/api/risk-score/route.ts` — empty file
- `maply/app/api/reports/route.ts` — empty file
- `maply/types/index.ts` — empty file
- `maply/components/SafetyMap.tsx` — 149-line presentational mock map (must preserve visual shell)
- `maply/components/map/Heatmap.tsx` — empty file
- `maply/components/map/SafeRoute.tsx` — empty file
- `maply/components/map/MapContainer.tsx` — basic Leaflet map with colored polylines
- Backend `RiskScoreAPI` loads CSVs and returns district/state-level `safety_score` + `risk_category`
- Backend chatbot endpoint `/api/v1/chatbot/explain` has no output guardrails against declaring zones "completely safe"

## Dependency Additions
Add to `maply/package.json` via `npm install`:
- `zustand@5.x` — global state
- `leaflet-routing-machine@3.2.12` — routing engine (peer dependency of `leaflet`)
- `@types/leaflet-routing-machine` (or a local type declaration if types package is stale)

Routing compatibility note: `leaflet-routing-machine` v3.2.12 is unmaintained and may not work cleanly with React 19 / `react-leaflet` v5. The plan therefore treats `leaflet-routing-machine` as the primary implementation but wraps it in a dynamic import and keeps a robust HTTP fallback to the OSRM public demo API (`https://router.project-osrm.org/route/v1/driving/{lon},{lat};...`) that returns a polyline. If `leaflet-routing-machine` fails at runtime, the fallback is used transparently.

No new Python dependencies required; use `scipy.spatial.distance`, standard library, and existing FastAPI/Pydantic.

## File Inventory

### Frontend Files Created/Modified
1. `maply/store/useStore.tsx` — Zustand store (create)
2. `maply/hooks/useLocation.ts` — geolocation hook (create)
3. `maply/hooks/useSOS.ts` — SOS streaming hook (create)
4. `maply/hooks/useNetwork.ts` — optional network-status hook; delete the existing typo file `maply/hooks/useNetwor.ts` (modify)
5. `maply/types/index.ts` — shared TypeScript types (create)
6. `maply/lib/api.ts` — uniform HTTP + WebSocket clients (create)
7. `maply/lib/geo.ts` — coordinate interpolation / segment helpers (create)
8. `maply/components/SafetyMap.tsx` — dynamic routing + floating search UI (modify)
9. `maply/components/map/Heatmap.tsx` — animated risk overlay layer (modify/create)
10. `maply/components/map/SafeRoute.tsx` — risk-colored polyline renderer (modify/create)
11. `maply/app/api/sos/route.ts` — Next.js light SOS validation proxy (create)
12. `maply/app/api/risk-score/route.ts` — Next.js light risk-score proxy (create)
13. `maply/app/api/reports/route.ts` — Next.js report submission handler (create)
14. `maply/components.json` / `tsconfig.json` — ensure path aliases `@/*` unchanged (read-only)

### Backend Files Modified
15. `ml_services/api/schemas.py` — add route-risk schemas (modify)
16. `ml_services/api/main.py` — add spatial route-risk endpoint (modify)
17. `ml_services/Risk_Score_Engine/model.py` — add nearest-district lookup (modify)
18. `ml_services/chatbot/api.py` — add safety guardrails (modify)

## Backend Spatial Mapping Design
- The XGBoost model is trained at the district/state level. There is no sub-district coordinate mapping.
- Spatial lookup strategy: nearest-neighbor on district centroid table.
- District centroids are generated at startup by geocoding every unique `(state, district)` pair from the loaded CSVs against a built-in static lookup table (`ml_services/Risk_Score_Engine/district_centroids.json`) that ships with the repository. If a district is missing from the lookup, we attempt a single Nominatim geocode request only when `geopy` is installed; otherwise we fall back to the centroid of the state (if known) or a default Indian centroid. The centroid cache is written to `ml_services/data/district_centroids.json` so subsequent startups are fast.
- For each route coordinate, find the 1-NN district using a `scipy.spatial.cKDTree` built on `[lat, lng]`.
- Convert backend `safety_score` (0-100, higher = safer) to risk score (0-1, higher = riskier): `risk_score = 1 - safety_score / 100`.
- Route endpoint returns `segments: [{lat, lng, risk_score, risk_category}]`.

## Chunks

### Chunk 1 — Shared Types & API Utilities
**Files:** `maply/types/index.ts`, `maply/lib/api.ts`, `maply/lib/geo.ts`
**Complexity:** simple
**Acceptance Criteria:**
- Types for `LatLng`, `RouteSegment`, `RiskTier`, `SOSPayload`, `AuthHeaders` exported.
- `api.ts` exports `apiGet`, `apiPost`, `getAuthHeaders` (mock JWT), and `FASTAPI_BASE_URL` env-aware.
- `geo.ts` exports `haversine`, `interpolateRoute`, and `chunkPolyline`.
- `tsc --noEmit` passes.

### Chunk 2 — Zustand Store
**File:** `maply/store/useStore.tsx`
**Complexity:** simple
**Acceptance Criteria:**
- Store tracks `userLocation`, `destinationLocation`, `currentRouteSegments`, `globalRiskTier`, `sosActive`, `activeWebSocketStatus`.
- Includes actions: `setUserLocation`, `setDestination`, `setRouteSegments`, `setGlobalRiskTier`, `setSOSActive`, `setWebSocketStatus`.
- Persists `sosActive` in `sessionStorage` so an SOS survives refresh.
- `tsc --noEmit` passes and store is importable from a component.

### Chunk 3 — Geolocation Hook
**File:** `maply/hooks/useLocation.ts`
**Complexity:** simple
**Acceptance Criteria:**
- Uses `navigator.geolocation.watchPosition` with `enableHighAccuracy: true`, `timeout: 10000`, `maximumAge: 5000`.
- Debounces updates at 500ms and writes to Zustand.
- Handles permission denied / unavailable with fallback to `DEFAULT_LOCATION`.
- Returns `{ location, error, permissionState, isWatching }`.
- Cleanup stops watcher on unmount.

### Chunk 4 — SOS Hook + Next.js Proxy
**Files:** `maply/hooks/useSOS.ts`, `maply/app/api/sos/route.ts`
**Complexity:** complex
**Concurrency/Resilience Primitives:**
- WebSocket connection to FastAPI route endpoint (to be added in chunk 7). If WebSocket unavailable, falls back to HTTP `POST /api/sos` with `navigator.sendBeacon` as last resort before unload.
- Exponential backoff reconnection: base delay 1s, max delay 30s, capped attempts, jitter via `Math.random() * 0.5`.
- WebSocket lifecycle: `connect()` creates `WebSocket` from `useRef`, registers `onopen/onmessage/onclose/onerror`, `disconnect()` closes and clears refs, cleanup on unmount or `sosActive=false`.
- Error propagation: socket errors are logged and trigger reconnect loop; HTTP fallback failures set `activeWebSocketStatus` to `error`.
**Acceptance Criteria:**
- Hook reads/writes `sosActive` in Zustand.
- On activate, immediately sends current location and then every 5s.
- Implements exponential backoff reconnect.
- Next.js proxy validates method, mocks JWT auth header, and forwards to FastAPI via HTTP (WebSocket cannot be proxied through Next.js Route Handler, so the client connects directly to FastAPI; route handler exists for the HTTP fallback path and auth handshake).

### Chunk 5 — Map Components (SafeRoute + Heatmap)
**Files:** `maply/components/map/SafeRoute.tsx`, `maply/components/map/Heatmap.tsx`
**Complexity:** simple
**Acceptance Criteria:**
- `SafeRoute` renders Leaflet polylines, one per segment, colored by risk score: `<0.3` green `#10B981`, `0.3-0.6` yellow `#F59E0B`, `>0.6` red `#EF4444`.
- `Heatmap` renders the same decorative animated risk zone circles already present in SafetyMap.tsx (green/orange/red blurred blobs). It does not consume a data endpoint; the decorative blobs preserve the existing UI aesthetic.

### Chunk 6 — SafetyMap Integration
**File:** `maply/components/SafetyMap.tsx`
**Complexity:** complex (Leaflet + routing + state integration, no goroutines)
**Design:**
- Preserve existing section, grid background, typography, blur gradients, and legend.
- Replace the static SVG mock map with a live `MapContainer` from `react-leaflet`.
- Add floating destination search bar using OSM Nominatim geocoding.
- Primary routing: dynamically import `leaflet-routing-machine` via `next/dynamic` and compute a route from `userLocation` to `destinationLocation`.
- Fallback routing: if `leaflet-routing-machine` fails or is unavailable, call OSRM public demo API (`https://router.project-osrm.org/route/v1/driving/{startLon},{startLat};{endLon},{endLat}?overview=full&geometries=polyline`) and decode the polyline.
- On route computed, sample coordinates every ~200m, call FastAPI `/api/v1/risk/route` (chunk 7), receive per-coordinate risk, build `RouteSegment[]`, store in Zustand.
- Display live user location marker and `SafeRoute` colored segments.
**Acceptance Criteria:**
- UI shell (grid background, legends, blur blobs) unchanged.
- Search bar floats at top of map, returns results, sets destination.
- Route updates when destination changes.
- No Next.js SSR errors.

### Chunk 7 — FastAPI Spatial Route Endpoint
**Files:** `ml_services/api/main.py`, `ml_services/api/schemas.py`, `ml_services/Risk_Score_Engine/model.py`
**Complexity:** complex (spatial algorithm + XGBoost integration)
**Algorithm:**
- Add `CoordinateRiskRequest` and `CoordinateRiskResponse` schemas.
- Add `POST /api/v1/risk/route` accepting `coordinates: List[Tuple[float,float]]`.
- Add `GET /api/v1/risk/coordinate?lat=&lng=` returning risk for a single coordinate.
- In `RiskScoreAPI`, build a `cKDTree` over district centroids generated from the built-in lookup table and CSV-derived district list; cache missing lookups to `data/district_centroids.json`.
- For each coordinate, find the 1-NN district, compute `risk_score = 1 - safety_score/100`, assign category.
- Return array matching input order.
- Add `WebSocket /ws/sos` endpoint: accepts JSON `{lat,lng,timestamp,token}`, validates token (mock JWT), acknowledges with `{status:"ok",received_at}`, and logs to the application logger. There is no consumer other than the server logger in this milestone; broadcasts are not required.
**Acceptance Criteria:**
- Endpoint returns risk per coordinate in <200ms for 100 points.
- Existing risk endpoints continue to work.
- `pytest ml_services/tests` passes.

### Chunk 8 — Chatbot Guardrails
**File:** `ml_services/chatbot/api.py`
**Complexity:** simple
**Acceptance Criteria:**
- Add `SAFETY_DENYLIST` regex patterns: `"completely safe"`, `"100% safe"`, `"no risk"`, `"perfectly safe"`, `"entirely safe"`, case-insensitive.
- Add `post_process_guardrails(text, risk_info)` that:
  - Removes/replaces absolute-safety claims by substituting the matched phrase with "has a reported safety score of {safety_score}/100, which is categorized as {risk_category}".
  - Appends a mandatory disclaimer to every explanation: "This assessment is based on reported data and is not a guarantee of safety."
- Apply post-processing to `explanation` before returning.
- Add unit test verifying guardrail triggers.

### Chunk 9 — Next.js Route Handlers (reports, risk-score)
**Files:** `maply/app/api/reports/route.ts`, `maply/app/api/risk-score/route.ts`
**Complexity:** simple
**Acceptance Criteria:**
- `POST /api/reports` validates body and forwards to FastAPI report endpoint (or stores locally if backend endpoint missing).
- `GET /api/risk-score?lat=&lng=` proxies to FastAPI `/api/v1/risk/coordinate` (added in chunk 7).
- Both enforce mock JWT header and return JSON.

### Chunk 10 — Test & Type Validation
**Files:** new test files; existing code
**Complexity:** simple
**Acceptance Criteria:**
- `npm install` succeeds in `maply/` and adds new deps to `package.json`.
- `npm run lint` passes in `maply/`.
- `tsc --noEmit` passes in `maply/`.
- `pytest ml_services/tests` passes.

## Ordering
1. Chunk 1 (types/utilities) → Chunk 2 (store) → Chunk 3 (geolocation) can run sequentially.
2. Chunk 4 (SOS) depends on Chunk 2.
3. Chunk 5 depends on Chunk 1.
4. Chunk 6 depends on Chunks 1, 2, 3, 5, 7.
5. Chunk 7 (FastAPI) and Chunk 8 (chatbot) are backend and can run in parallel with frontend Chunks 1-5.
6. Chunk 9 (Next.js handlers) depends on Chunk 7.
7. Chunk 10 runs last.

## Risk & Constraints
- No placeholders. Every function fully implemented with fallbacks.
- Tailwind CSS shell in SafetyMap.tsx must be preserved.
- Heavy routing/scoring bypasses Next.js serverless limits by calling FastAPI directly from the client.
- WebSocket for SOS connects client ↔ FastAPI directly; Next.js route handler is only an HTTP fallback.

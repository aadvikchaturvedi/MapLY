# Plan Verdict: Navigation Integration Plan

**Verdict:** NEEDS_REVISION

The plan is directionally aligned with the original task, but it contains endpoint mismatches, missing data sources, and unmitigated dependency risks that would block a clean build without mid-implementation clarification.

---

## Chunk-by-Chunk Review

### Chunk 1 — Shared Types & API Utilities
- **Feasibility:** Buildable
- **Complexity:** simple
- Notes: Pure TypeScript types and HTTP helpers. `FASTAPI_BASE_URL` env handling and mock JWT headers are straightforward. No concurrency primitives.

### Chunk 2 — Zustand Store
- **Feasibility:** Buildable with care
- **Complexity:** simple
- Notes: State shape and actions are well-defined. `sessionStorage` persistence must be guarded against SSR/hydration in Next.js, but this is an implementation detail, not a plan blocker.

### Chunk 3 — Geolocation Hook
- **Feasibility:** Buildable
- **Complexity:** simple
- Notes: Standard `navigator.geolocation.watchPosition` usage with debounce and fallback. No concurrency primitives beyond the browser geolocation callback.

### Chunk 4 — SOS Hook + Next.js Proxy
- **Feasibility:** Buildable but error-prone
- **Complexity:** complex (MANDATORY)
- Notes: Uses WebSocket lifecycle, exponential backoff reconnection loop with jitter, `navigator.sendBeacon`, and ref-based cleanup. This is state-machine-style logic and must be classified as complex. The ordering correctly lets this run in parallel with backend chunk 7, but integration cannot be fully tested until `/ws/sos` exists.

### Chunk 5 — Map Components (SafeRoute + Heatmap)
- **Feasibility:** Buildable
- **Complexity:** simple
- Notes: Leaflet polylines and animated CSS circles are straightforward. However, the plan does not specify the data source or shape for `Heatmap` risk zones (see gaps below).

### Chunk 6 — SafetyMap Integration
- **Feasibility:** Risky / needs mitigation
- **Complexity:** complex (MANDATORY)
- Notes: `leaflet-routing-machine` v3.2.12 is unmaintained and has not been verified against Next.js 16, React 19, and `react-leaflet` v5. It also relies on an unspecified routing backend (public OSRM demo server by default), which has rate limits and poor India coverage. Internally, routing machines use graph algorithms, so this chunk must be classified as complex. Dynamic import solves SSR issues but not runtime compatibility or backend availability.

### Chunk 7 — FastAPI Spatial Route Endpoint
- **Feasibility:** Buildable with data caveat
- **Complexity:** complex (MANDATORY)
- Notes: KDTree / nearest-neighbor lookup over district centroids is a spatial algorithm, and the chunk adds a WebSocket endpoint, so it must be classified as complex. Performance target (<200 ms for 100 points) is easily met. The main risk is the absence of `district_centroids.json` or any coordinate data in the current CSVs; the fallback to a static metro list gives demo-only coverage.

### Chunk 8 — Chatbot Guardrails
- **Feasibility:** Buildable
- **Complexity:** simple
- Notes: Regex denylist and post-processing are simple. The acceptance criterion that appends a disclaimer only when `safety_score > 80` is semantically odd (higher score means safer), but it is implementable.

### Chunk 9 — Next.js Route Handlers (reports, risk-score)
- **Feasibility:** Buildable but endpoint mismatch
- **Complexity:** simple
- Notes: Proxies are simple. However, the plan says `GET /api/risk-score?lat=&lng=` proxies to FastAPI `/api/v1/risk/coordinate`, but chunk 7 never defines `/api/v1/risk/coordinate`; it defines `POST /api/v1/risk/route`. This is a plan-level gap that must be resolved before implementation.

### Chunk 10 — Test & Type Validation
- **Feasibility:** Buildable
- **Complexity:** simple
- Notes: lint, `tsc --noEmit`, and `pytest` are standard gates. Feasibility depends on earlier chunks resolving the issues noted above.

---

## Gaps Requiring Revision

1. **Missing `/api/v1/risk/coordinate` endpoint**
   - Chunk 9 references `/api/v1/risk/coordinate`, but only `POST /api/v1/risk/route` is defined in chunk 7.
   - Revision needed: Either add `GET /api/v1/risk/coordinate` to chunk 7 or change chunk 9 to call `/api/v1/risk/route` with a single coordinate.

2. **Unverified `leaflet-routing-machine` compatibility**
   - The current `maply/package.json` uses Next.js 16.1.2, React 19.2.3, and `react-leaflet` 5.0.0. `leaflet-routing-machine` 3.2.12 predates these versions and may fail at runtime.
   - Revision needed: Add a spike/POC step to verify integration or nominate an alternative routing library. Specify the routing backend (e.g., self-hosted OSRM, Valhalla, or Mapbox) instead of defaulting to the public OSRM demo.

3. **District centroid data source is not available**
   - The current `data/` directory only contains crime CSVs with state/district names but no coordinates. `district_centroids.json` does not exist.
   - Revision needed: Specify how centroids are generated (e.g., geocode all districts from CSVs at startup, bundle a GeoJSON, or accept the limited static fallback). The current fallback to "major Indian metro centroids" will not cover most districts in the dataset.

4. **Heatmap data source is undefined**
   - Chunk 5 says `Heatmap` should render animated risk zone circles, but no endpoint returns zone polygons or coordinates for a data-driven overlay.
   - Revision needed: Clarify whether the heatmap remains decorative (matching the current static blobs) or should consume a new endpoint such as `/api/v1/risk/zones`.

5. **Ambiguous `useNetwor.ts` handling**
   - The file inventory lists `maply/hooks/useNetwor.ts` with a note "renamed? decide final name / fix typo (modify)". The plan does not commit to a final name.
   - Revision needed: State the final hook name (e.g., `useNetwork.ts`) and whether it is kept, renamed, or deleted.

6. **Guardrail disclaimer condition is counterintuitive**
   - Chunk 8 mandates a disclaimer when `safety_score > 80`. Because the score scale is "higher = safer", this attaches a warning to the safest-rated zones rather than to absolute-safety claims.
   - Revision needed: Make the disclaimer unconditional or trigger it when the explanation contains absolute-safety language after denylist filtering.

7. **WebSocket broadcast scope is unspecified**
   - Chunk 7 says `/ws/sos` should "broadcast/acknowledge" but does not define the consumer (e.g., an admin dashboard, a backend logger, or another client).
   - Revision needed: Define who receives broadcasts and whether any persistent store or pub/sub mechanism is required.

---

## Summary

Approve the overall architecture once the following are addressed:
- Fix the `/api/v1/risk/coordinate` mismatch.
- Validate or replace `leaflet-routing-machine` for the current React/Next.js stack and specify the routing backend.
- Resolve district centroid sourcing.
- Clarify heatmap data source and `useNetwor.ts` fate.
- Correct the chatbot disclaimer condition.

Until then, the plan should be revised before implementation begins.

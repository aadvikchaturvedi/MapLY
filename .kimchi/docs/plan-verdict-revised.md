# Plan Verdict — Revised Navigation Integration Plan

**Verdict:** APPROVED

The revised plan resolves the blocking issues from the previous review. The routing fallback strategy, centroid source, heatmap scope, FastAPI coordinate endpoint, chatbot guardrails, and file-inventory cleanup are now sufficiently specified to begin implementation.

## Remaining Gaps (non-blocking)

1. **Centroid file path ambiguity**  
   The plan names two different paths for the district centroid data:
   - Built-in static lookup: `ml_services/Risk_Score_Engine/district_centroids.json`
   - Runtime cache: `ml_services/data/district_centroids.json`
   Clarify whether these are the same file, or whether the built-in file is read-only and the runtime cache is a separate writable merge of static + geocoded results.

2. **Nominatim usage policy not specified**  
   The fallback to Nominatim geocoding requires a custom `User-Agent`, request throttling, and a caching strategy to comply with OSM's usage policy and avoid rate-limiting. Add these constraints to the implementation notes.

3. **OSRM public demo API not production-grade**  
   The OSRM demo server (`router.project-osrm.org`) has usage limits and no SLA. Because the objective calls the system "production-ready", the plan should explicitly flag this as a demo/dev fallback and list the criteria for swapping in a self-hosted or licensed routing service later.

4. **Reports route fallback is vague**  
   "forwards to FastAPI report endpoint (or stores locally if backend endpoint missing)" should define the local storage mechanism (e.g., `localStorage`, an on-disk JSON file, or a queue) and the reconciliation behavior when the backend becomes available.

5. **WebSocket CORS / origin policy**  
   Because the frontend opens a direct WebSocket to FastAPI, the plan should note that the backend must allow the frontend origin. FastAPI WebSockets do not use the CORS middleware, so any origin validation must be handled inside the `WebSocket` accept logic or at the reverse-proxy layer.

These items can be tightened during implementation and do not prevent approving the revised plan.

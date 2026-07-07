"use client";

/**
 * MapLY global client store.
 *
 * Holds runtime navigation state shared across components: the user's live
 * location, the selected destination, the currently rendered risk-coloured
 * route, the derived global risk tier, the SOS activation flag, and the
 * SOS WebSocket lifecycle status.
 *
 * Persistence:
 *   Only `sosActive` is persisted to `sessionStorage` so an in-progress
 *   SOS survives a page refresh but is cleared when the browser tab is
 *   closed. All other state is intentionally ephemeral.
 *
 * SSR:
 *   The store is safe to import on the server. The sessionStorage adapter
 *   is only constructed when `window` is defined; otherwise persistence is
 *   a no-op.
 */

import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import type {
  DestinationLocation,
  RiskTier,
  RouteSegment,
  UserLocation,
  WebSocketStatus,
} from "@/types";

/** Numeric severity ordering used to pick the worst tier in a route. */
const RISK_SEVERITY: Record<RiskTier, number> = {
  low: 0,
  moderate: 1,
  high: 2,
};

/**
 * No-op storage used during SSR so the persist middleware always
 * receives a `StateStorage`-shaped object. On the server `sessionStorage`
 * is unavailable, but persist is effectively disabled.
 */
const ssrStorage = {
  getItem: () => null,
  setItem: () => undefined,
  removeItem: () => undefined,
};

/**
 * Compute the highest-severity risk tier present across the supplied route
 * segments. Returns `"low"` for an empty or missing route so the UI has a
 * safe default (rendered as green).
 */
function deriveGlobalRiskTier(segments: RouteSegment[]): RiskTier {
  if (!segments || segments.length === 0) return "low";
  let worst: RiskTier = "low";
  for (const segment of segments) {
    const tier = segment?.risk_category ?? "low";
    if (RISK_SEVERITY[tier] > RISK_SEVERITY[worst]) {
      worst = tier;
    }
  }
  return worst;
}

export interface MaplyState {
  userLocation: UserLocation | null;
  destinationLocation: DestinationLocation | null;
  currentRouteSegments: RouteSegment[];
  globalRiskTier: RiskTier;
  sosActive: boolean;
  activeWebSocketStatus: WebSocketStatus;
}

export interface MaplyActions {
  setUserLocation: (location: UserLocation | null) => void;
  setDestination: (destination: DestinationLocation | null) => void;
  setRouteSegments: (segments: RouteSegment[]) => void;
  setGlobalRiskTier: (tier: RiskTier) => void;
  setSOSActive: (active: boolean) => void;
  setWebSocketStatus: (status: WebSocketStatus) => void;
}

export type MaplyStore = MaplyState & MaplyActions;

export const useStore = create<MaplyStore>()(
  persist(
    (set) => ({
      userLocation: null,
      destinationLocation: null,
      currentRouteSegments: [],
      globalRiskTier: "low",
      sosActive: false,
      activeWebSocketStatus: "idle",

      setUserLocation: (location) => set({ userLocation: location }),

      setDestination: (destination) => set({ destinationLocation: destination }),

      setRouteSegments: (segments) =>
        set({
          currentRouteSegments: segments,
          globalRiskTier: deriveGlobalRiskTier(segments),
        }),

      setGlobalRiskTier: (tier) => set({ globalRiskTier: tier }),

      setSOSActive: (active) => set({ sosActive: active }),

      setWebSocketStatus: (status) => set({ activeWebSocketStatus: status }),
    }),
    {
      name: "maply-store",
      storage: createJSONStorage(() =>
        typeof window === "undefined" ? ssrStorage : window.sessionStorage
      ),
      partialize: (state) => ({ sosActive: state.sosActive }),
    }
  )
);

export default useStore;

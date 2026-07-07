"use client";

/**
 * Client-side hook that streams the browser's geolocation into the
 * MapLY zustand store via `setUserLocation`.
 *
 * Behaviour:
 *   - Calls `navigator.geolocation.watchPosition` with
 *     `enableHighAccuracy: true`, `timeout: 10000`, `maximumAge: 5000`.
 *   - Debounces incoming position updates by 500 ms before pushing
 *     them into the store, so a flurry of fix samples does not flood
 *     React subscribers.
 *   - On `PERMISSION_DENIED` / `POSITION_UNAVAILABLE` / `TIMEOUT` it
 *     falls back to `DEFAULT_LOCATION` (New Delhi) and surfaces a
 *     human-readable error.
 *   - SSR-safe: when `window` is undefined the hook returns safe
 *     defaults and does not attempt to touch the geolocation API.
 *   - The watcher and any pending debounce timer are torn down on
 *     unmount.
 */

import { useEffect, useRef, useState } from "react";

import { useStore } from "@/store/useStore";
import type { UserLocation } from "@/types";

/** New Delhi — used as a graceful fallback when geolocation fails. */
export const DEFAULT_LOCATION: UserLocation = {
  lat: 28.61,
  lng: 77.2,
  accuracy: undefined,
  heading: undefined,
  speed: undefined,
  timestamp: Date.now(),
};

const DEBOUNCE_MS = 500;
const GEO_TIMEOUT_MS = 10_000;
const GEO_MAX_AGE_MS = 5_000;

/** Browser permission state, mirrored into hook state. */
export type PermissionState = "unknown" | "granted" | "denied" | "prompt";

export interface UseLocationResult {
  location: UserLocation | null;
  error: string | null;
  permissionState: PermissionState;
  isWatching: boolean;
}

const SSR_DEFAULTS: UseLocationResult = {
  location: null,
  error: null,
  permissionState: "unknown",
  isWatching: false,
};

function describeError(code: number): string {
  switch (code) {
    case 1:
      return "Geolocation permission denied.";
    case 2:
      return "Geolocation position unavailable.";
    case 3:
      return "Geolocation request timed out.";
    default:
      return "Unknown geolocation error.";
  }
}

function toUserLocation(position: GeolocationPosition): UserLocation {
  return {
    lat: position.coords.latitude,
    lng: position.coords.longitude,
    accuracy: position.coords.accuracy,
    heading:
      position.coords.heading ?? undefined,
    speed: position.coords.speed ?? undefined,
    timestamp: position.timestamp,
  };
}

export function useLocation(): UseLocationResult {
  // Hard SSR guard: never touch `window`/`navigator` on the server.
  if (typeof window === "undefined") {
    return SSR_DEFAULTS;
  }

  const [location, setLocation] = useState<UserLocation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [permissionState, setPermissionState] =
    useState<PermissionState>("unknown");
  const [isWatching, setIsWatching] = useState<boolean>(false);

  // Latest position seen from the browser, not yet flushed to the store.
  const pendingPositionRef = useRef<GeolocationPosition | null>(null);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const watchIdRef = useRef<number | null>(null);
  const fallbackAppliedRef = useRef<boolean>(false);

  useEffect(() => {
    // Probe the Permissions API if available to enrich `permissionState`.
    let cancelled = false;
    const permissionsApi = (
      navigator as Navigator & {
        permissions?: { query: (q: { name: string }) => Promise<PermissionStatus> };
      }
    ).permissions;

    if (permissionsApi && typeof permissionsApi.query === "function") {
      permissionsApi
        .query({ name: "geolocation" })
        .then((status) => {
          if (cancelled) return;
          setPermissionState(
            status.state as PermissionState
          );
          status.onchange = () => {
            if (cancelled) return;
            setPermissionState(status.state as PermissionState);
          };
        })
        .catch(() => {
          /* Permissions API not supported for geolocation — leave as "unknown". */
        });
    }

    if (typeof navigator === "undefined" || !navigator.geolocation) {
      setError("Geolocation is not supported by this browser.");
      setPermissionState("denied");
      if (!fallbackAppliedRef.current) {
        useStore.getState().setUserLocation(DEFAULT_LOCATION);
        setLocation(DEFAULT_LOCATION);
        fallbackAppliedRef.current = true;
      }
      return () => {
        cancelled = true;
      };
    }

    const flushPending = () => {
      const next = pendingPositionRef.current;
      pendingPositionRef.current = null;
      debounceTimerRef.current = null;
      if (next) {
        const userLoc = toUserLocation(next);
        setLocation(userLoc);
        setError(null);
        useStore.getState().setUserLocation(userLoc);
      }
    };

    const handleSuccess = (position: GeolocationPosition) => {
      setPermissionState("granted");
      pendingPositionRef.current = position;
      if (debounceTimerRef.current === null) {
        debounceTimerRef.current = setTimeout(flushPending, DEBOUNCE_MS);
      }
    };

    const handleError = (err: GeolocationPositionError) => {
      setError(describeError(err.code));
      if (err.code === 1) {
        setPermissionState("denied");
      }
      if (!fallbackAppliedRef.current) {
        useStore.getState().setUserLocation(DEFAULT_LOCATION);
        setLocation(DEFAULT_LOCATION);
        fallbackAppliedRef.current = true;
      }
    };

    watchIdRef.current = navigator.geolocation.watchPosition(
      handleSuccess,
      handleError,
      {
        enableHighAccuracy: true,
        timeout: GEO_TIMEOUT_MS,
        maximumAge: GEO_MAX_AGE_MS,
      }
    );
    setIsWatching(true);

    return () => {
      cancelled = true;
      setIsWatching(false);
      if (watchIdRef.current !== null && navigator.geolocation) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
      watchIdRef.current = null;
      if (debounceTimerRef.current !== null) {
        clearTimeout(debounceTimerRef.current);
      }
      debounceTimerRef.current = null;
      pendingPositionRef.current = null;
    };
  }, []);

  return { location, error, permissionState, isWatching };
}

export default useLocation;

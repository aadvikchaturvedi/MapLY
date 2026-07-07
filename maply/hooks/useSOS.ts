"use client";

/**
 * useSOS
 *
 * Streams the user's live location to the MapLY FastAPI SOS endpoint
 * (`/ws/sos`) while `sosActive` is true in the Zustand store.
 *
 * Transport selection:
 *   - Primary: WebSocket connected directly to FastAPI (Next.js Route
 *     Handlers cannot proxy WebSockets). The URL is derived from
 *     `FASTAPI_BASE_URL` by swapping the `http(s)` scheme for `ws(s)`.
 *   - Fallback: HTTP `POST` to the local Next.js route `/api/sos` when
 *     the socket cannot be opened or is no longer `OPEN`.
 *   - Last-resort: `navigator.sendBeacon('/api/sos', blob)` fired on
 *     `pagehide` / `beforeunload` / `visibilitychange=hidden` so a
 *     location update makes it to the server even if the browser tears
 *     the page down before the regular send loop runs.
 *
 * Resilience:
 *   - Reconnects with exponential backoff (base 1s, max 30s, capped at
 *     10 attempts, jitter `Math.random() * 0.5`) while the hook is
 *     active. Reaching the cap marks the socket as `error` and stops
 *     further reconnects; the HTTP fallback path still fires.
 *   - On unmount or `sosActive=false`, the socket is closed, all
 *     timers cleared, and the WebSocket status reset to `idle`.
 */

import { useEffect, useRef } from "react";

import { FASTAPI_BASE_URL } from "@/lib/api";
import { useStore } from "@/store/useStore";
import type { SOSPayload, UserLocation } from "@/types";

/** Mock JWT used by both WebSocket and HTTP fallback paths. */
const MOCK_JWT_TOKEN = "mock-jwt-token";

/** Cadence at which an active SOS re-streams the current location. */
const SOS_SEND_INTERVAL_MS = 5_000;

/** Reconnect backoff parameters. */
const RECONNECT_BASE_MS = 1_000;
const RECONNECT_MAX_MS = 30_000;
const RECONNECT_MAX_ATTEMPTS = 10;

/** Relative path of the Next.js HTTP fallback route. */
const SOS_HTTP_FALLBACK_PATH = "/api/sos";

/** Next.js WebSocket URL path on the FastAPI backend. */
const FASTAPI_WS_PATH = "/ws/sos";

/**
 * Compute the next reconnect delay with exponential backoff and jitter.
 * `attempt` is zero-based; the result is bounded by `RECONNECT_MAX_MS`.
 */
function nextBackoffMs(attempt: number): number {
  const exp = Math.min(
    RECONNECT_BASE_MS * Math.pow(2, attempt),
    RECONNECT_MAX_MS
  );
  return exp * (1 + Math.random() * 0.5);
}

/**
 * Build an `SOSPayload` from the current user location. Returns `null`
 * when no usable location is available (e.g. permission denied and no
 * fallback) so the caller can skip the send rather than emit garbage.
 */
function buildPayload(location: UserLocation | null): SOSPayload | null {
  if (!location) return null;
  if (
    !Number.isFinite(location.lat) ||
    !Number.isFinite(location.lng) ||
    Math.abs(location.lat) > 90 ||
    Math.abs(location.lng) > 180
  ) {
    return null;
  }
  return {
    lat: location.lat,
    lng: location.lng,
    timestamp: Date.now(),
    token: MOCK_JWT_TOKEN,
  };
}

/**
 * Best-effort beacon transmission. Returns whether the browser accepted
 * the payload for delivery; the call is fire-and-forget.
 */
function sendBeacon(payload: SOSPayload): boolean {
  if (typeof navigator === "undefined") return false;
  if (typeof navigator.sendBeacon !== "function") return false;
  try {
    const blob = new Blob([JSON.stringify(payload)], {
      type: "application/json",
    });
    return navigator.sendBeacon(SOS_HTTP_FALLBACK_PATH, blob);
  } catch {
    return false;
  }
}

/**
 * HTTP POST fallback. Resolves regardless of server response so the
 * caller never throws into a timer or socket callback. Network failures
 * are reported via `setWebSocketStatus("error")` only on transport
 * errors (not on non-2xx, which the server may legitimately emit while
 * it boots).
 */
async function sendViaHttp(
  payload: SOSPayload,
  onTransportError: () => void
): Promise<void> {
  try {
    const response = await fetch(SOS_HTTP_FALLBACK_PATH, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      keepalive: true,
    });
    if (!response.ok) {
      onTransportError();
    }
  } catch {
    onTransportError();
  }
}

/**
 * Build the FastAPI WebSocket URL from the configured HTTP base URL by
 * swapping the scheme prefix. Works for both `http://` and `https://`.
 */
function buildWebSocketUrl(): string {
  return FASTAPI_BASE_URL.replace(/^http/, "ws") + FASTAPI_WS_PATH;
}

export function useSOS(): void {
  const sosActive = useStore((s) => s.sosActive);
  const setWebSocketStatus = useStore((s) => s.setWebSocketStatus);

  // Mutable refs survive renders and avoid stale closures inside
  // socket callbacks and timers.
  const wsRef = useRef<WebSocket | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(
    null
  );
  const reconnectAttemptRef = useRef(0);
  const locationRef = useRef<UserLocation | null>(
    useStore.getState().userLocation
  );
  const activeRef = useRef(sosActive);
  const unmountedRef = useRef(false);

  // Mirror the latest user location into a ref so the send loop and
  // socket callbacks always read fresh coordinates without having to
  // tear down the connection every time the user moves.
  useEffect(() => {
    locationRef.current = useStore.getState().userLocation;
    const unsubscribe = useStore.subscribe((state) => {
      locationRef.current = state.userLocation;
    });
    return unsubscribe;
  }, []);

  const markTransportError = (): void => {
    setWebSocketStatus("error");
  };

  /**
   * Send the current location immediately. Prefers the live WebSocket
   * when it is `OPEN`; otherwise falls back to a single HTTP POST.
   */
  const sendNow = (): void => {
    if (!activeRef.current || unmountedRef.current) return;
    const payload = buildPayload(locationRef.current);
    if (!payload) return;

    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      try {
        ws.send(JSON.stringify(payload));
        return;
      } catch {
        // Drop to HTTP fallback if the send itself throws.
      }
    }
    void sendViaHttp(payload, markTransportError);
  };

  const clearTimers = (): void => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (reconnectTimeoutRef.current !== null) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  };

  const closeSocket = (): void => {
    const ws = wsRef.current;
    if (!ws) return;
    wsRef.current = null;
    try {
      // Detach handlers so the intentional close does not trigger a
      // reconnect cycle from the `onclose` callback below.
      ws.onopen = null;
      ws.onmessage = null;
      ws.onerror = null;
      ws.onclose = null;
      if (
        ws.readyState === WebSocket.OPEN ||
        ws.readyState === WebSocket.CONNECTING
      ) {
        ws.close();
      }
    } catch {
      // ignore close failures
    }
  };

  const scheduleReconnect = (): void => {
    if (unmountedRef.current || !activeRef.current) return;
    if (reconnectAttemptRef.current >= RECONNECT_MAX_ATTEMPTS) {
      setWebSocketStatus("error");
      return;
    }
    const attempt = reconnectAttemptRef.current;
    reconnectAttemptRef.current = attempt + 1;
    const delay = nextBackoffMs(attempt);
    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectTimeoutRef.current = null;
      connect();
    }, delay);
  };

  const connect = (): void => {
    if (unmountedRef.current || !activeRef.current) return;
    if (wsRef.current) return; // already connecting/open

    setWebSocketStatus("connecting");

    let ws: WebSocket;
    try {
      ws = new WebSocket(buildWebSocketUrl());
    } catch {
      // Constructor failed (e.g. invalid URL). Send one immediate HTTP
      // heartbeat so the user is not stranded and try to reconnect.
      setWebSocketStatus("error");
      const payload = buildPayload(locationRef.current);
      if (payload) void sendViaHttp(payload, markTransportError);
      scheduleReconnect();
      return;
    }

    wsRef.current = ws;

    ws.onopen = () => {
      if (unmountedRef.current || !activeRef.current) {
        try {
          ws.close();
        } catch {
          // ignore
        }
        return;
      }
      reconnectAttemptRef.current = 0;
      setWebSocketStatus("open");
      sendNow();
    };

    ws.onmessage = () => {
      // Backend currently only logs inbound SOS frames. Hook retained so
      // a future broadcast/control channel can update UI state here.
    };

    ws.onerror = () => {
      // The `close` event will fire after `error`; let it drive
      // reconnect so we don't double-schedule.
      if (!unmountedRef.current && activeRef.current) {
        setWebSocketStatus("error");
      }
    };

    ws.onclose = () => {
      wsRef.current = null;
      if (unmountedRef.current || !activeRef.current) {
        setWebSocketStatus("idle");
        return;
      }
      setWebSocketStatus("closed");
      scheduleReconnect();
    };
  };

  // Lifecycle effect: drive connect/cleanup on `sosActive` changes.
  useEffect(() => {
    if (typeof window === "undefined") return;

    // Reset the unmount guard so a deactivation -> reactivation cycle
    // (e.g. user toggles SOS off and on again) re-arms cleanly.
    unmountedRef.current = false;
    activeRef.current = sosActive;

    if (!sosActive) {
      clearTimers();
      closeSocket();
      setWebSocketStatus("idle");
      return;
    }

    // Activate.
    reconnectAttemptRef.current = 0;
    connect();

    intervalRef.current = setInterval(() => {
      sendNow();
    }, SOS_SEND_INTERVAL_MS);

    const handlePageHide = (): void => {
      const payload = buildPayload(locationRef.current);
      if (payload) sendBeacon(payload);
    };

    const handleVisibilityChange = (): void => {
      if (
        typeof document !== "undefined" &&
        document.visibilityState === "hidden"
      ) {
        handlePageHide();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("pagehide", handlePageHide);
    window.addEventListener("beforeunload", handlePageHide);

    return () => {
      unmountedRef.current = true;
      activeRef.current = false;
      clearTimers();
      closeSocket();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("pagehide", handlePageHide);
      window.removeEventListener("beforeunload", handlePageHide);
    };
    // The lifecycle effect intentionally keys on `sosActive` only;
    // internal helpers read from refs to stay current.
  }, [sosActive, setWebSocketStatus]);
}

export default useSOS;

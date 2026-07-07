/**
 * Thin HTTP client for talking to the MapLY FastAPI backend.
 *
 * Every request goes through `apiGet` / `apiPost` so that authentication
 * headers and base URL handling stay in one place. The backend lives at
 * `NEXT_PUBLIC_FASTAPI_URL` in the browser environment, with a sensible
 * local default for development.
 */

import type { AuthHeaders } from "@/types";
import { cacheGet, cacheSet } from "@/lib/cache";

/**
 * Base URL for all FastAPI requests. Configured via the
 * `NEXT_PUBLIC_FASTAPI_URL` environment variable; falls back to
 * `http://localhost:8000` (the uvicorn default) when unset.
 *
 * Trailing slashes are stripped so callers can safely concatenate paths.
 */
export const FASTAPI_BASE_URL: string = (
  process.env.NEXT_PUBLIC_FASTAPI_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");

/**
 * Build the set of authorization headers attached to every request.
 * Currently a mock implementation; production will swap the literal
 * JWT for the real session token.
 */
export function getAuthHeaders(): AuthHeaders {
  return {
    Authorization: "Bearer mock-jwt-token",
    "x-maply-client": "web",
  };
}

/** Primitive JSON value accepted as a request body. */
export type JsonBody = Record<string, unknown> | unknown[] | null;

/** Optional query parameters, encoded as `?k=v&...`. */
export type QueryParams = Record<
  string,
  string | number | boolean | null | undefined
>;

/**
 * Build a fully-qualified URL from a relative `path` and optional
 * `query` object. Returns just the base URL when `path` is empty.
 */
export function buildUrl(path: string, query?: QueryParams): string {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const base = `${FASTAPI_BASE_URL}${cleanPath}`;
  if (!query) return base;

  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === null || value === undefined) continue;
    search.append(key, String(value));
  }
  const qs = search.toString();
  return qs ? `${base}?${qs}` : base;
}

/**
 * Internal helper that performs a `fetch` with the standard auth
 * headers attached and a sane JSON default. Throws on non-2xx
 * responses with the body included for debugging.
 */
async function request<T>(
  path: string,
  init: RequestInit & { query?: QueryParams } = {}
): Promise<T> {
  const { query, headers, ...rest } = init;
  const url = buildUrl(path, query);

  const mergedHeaders: Record<string, string> = {
    Accept: "application/json",
    ...(rest.body !== undefined ? { "Content-Type": "application/json" } : {}),
    ...getAuthHeaders(),
    ...(headers as Record<string, string> | undefined),
  };

  const isRead = (init.method ?? "GET") === "GET";
  const cacheKey = isRead ? url : "";
  const cached = cacheKey ? cacheGet<T>(cacheKey) : undefined;
  if (cached) return cached;

  const response = await fetch(url, {
    ...rest,
    headers: mergedHeaders,
    cache: isRead ? "default" : "no-store",
  });

  if (!response.ok) {
    let detail = "";
    try {
      detail = await response.text();
    } catch {
      // ignore body read errors
    }
    throw new Error(
      `API ${init.method ?? "GET"} ${url} failed: ${response.status} ${response.statusText}${
        detail ? ` — ${detail}` : ""
      }`
    );
  }

  // 204 No Content
  if (response.status === 204) return undefined as T;

  const json = (await response.json()) as T;
  if (cacheKey) cacheSet(cacheKey, json);
  return json;
}

/**
 * Issue a `GET` request to the FastAPI backend. `query` is appended as
 * URL search parameters. Returns the parsed JSON response.
 */
export function apiGet<T = unknown>(
  path: string,
  query?: QueryParams
): Promise<T> {
  return request<T>(path, { method: "GET", query });
}

/**
 * Issue a `POST` request with a JSON `body`. The body is serialized
 * with `JSON.stringify`; pass `null` to send an empty JSON payload.
 */
export function apiPost<T = unknown>(
  path: string,
  body?: JsonBody
): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

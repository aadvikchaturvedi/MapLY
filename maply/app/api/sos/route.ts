import { NextRequest, NextResponse } from "next/server";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const { lat, lng, timestamp, token } = body;

    if (
      typeof lat !== "number" ||
      typeof lng !== "number" ||
      Math.abs(lat) > 90 ||
      Math.abs(lng) > 180
    ) {
      return NextResponse.json(
        { status: "error", message: "Invalid coordinates" },
        { status: 400 }
      );
    }

    const fastApiPayload = {
      lat,
      lng,
      timestamp: timestamp ?? Date.now(),
      token: token ?? "mock-jwt-token",
    };

    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/sos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(fastApiPayload),
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      const detail = await response.text().catch(() => "");
      return NextResponse.json(
        { status: "error", message: `FastAPI upstream error: ${response.status}${detail ? ` — ${detail}` : ""}` },
        { status: response.status }
      );
    }

    const data = await response.json().catch(() => ({}));
    return NextResponse.json({ status: "ok", received_at: data.received_at ?? new Date().toISOString() });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Internal server error";
    return NextResponse.json(
      { status: "error", message },
      { status: 500 }
    );
  }
}

import { NextRequest, NextResponse } from "next/server";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { lat, lng, category, description } = body;

    if (typeof lat !== "number" || typeof lng !== "number") {
      return NextResponse.json(
        { status: "error", message: "lat and lng are required numbers" },
        { status: 400 }
      );
    }

    if (Math.abs(lat) > 90 || Math.abs(lng) > 180) {
      return NextResponse.json(
        { status: "error", message: "Coordinates out of range" },
        { status: 400 }
      );
    }

    const payload = {
      lat,
      lng,
      category: category ?? "general",
      description: description ?? "",
      timestamp: Date.now(),
    };

    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/reports`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      const detail = await response.text().catch(() => "");
      return NextResponse.json(
        { status: "error", message: `Upstream error: ${response.status}${detail ? ` — ${detail}` : ""}` },
        { status: response.status }
      );
    }

    const data = await response.json().catch(() => ({}));
    return NextResponse.json({ status: "ok", id: data.id ?? null, created_at: data.created_at ?? new Date().toISOString() });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Internal server error";
    return NextResponse.json(
      { status: "error", message },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const lat = searchParams.get("lat");
    const lng = searchParams.get("lng");
    const radius = searchParams.get("radius") ?? "1000";

    const query = new URLSearchParams();
    if (lat) query.set("lat", lat);
    if (lng) query.set("lng", lng);
    query.set("radius", radius);

    const response = await fetch(
      `${FASTAPI_BASE_URL}/api/v1/reports?${query.toString()}`,
      { signal: AbortSignal.timeout(5000) }
    );

    if (!response.ok) {
      return NextResponse.json(
        { status: "error", message: `Upstream error: ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Internal server error";
    return NextResponse.json(
      { status: "error", message },
      { status: 500 }
    );
  }
}

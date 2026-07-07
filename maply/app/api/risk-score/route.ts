import { NextRequest, NextResponse } from "next/server";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_URL ?? "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const state = searchParams.get("state");
    const district = searchParams.get("district");

    if (!state || !district) {
      return NextResponse.json(
        { status: "error", message: "state and district query params required" },
        { status: 400 }
      );
    }

    const url = `${FASTAPI_BASE_URL}/api/v1/risk/location?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}`;
    const response = await fetch(url, { signal: AbortSignal.timeout(5000) });

    if (!response.ok) {
      return NextResponse.json(
        { safety_score: 0, risk_category: "Unknown", is_fallback: true },
        { status: 200 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { safety_score: 0, risk_category: "Unknown", is_fallback: true },
      { status: 200 }
    );
  }
}

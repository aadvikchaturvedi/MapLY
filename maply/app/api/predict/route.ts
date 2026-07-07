import { NextRequest, NextResponse } from "next/server";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { state, district } = body;

    if (!state || !district) {
      return NextResponse.json(
        {
          status: "error",
          message: "state and district are required",
          risk_category: "Unknown",
          safety_score: 0,
          is_fallback: true,
        },
        { status: 400 }
      );
    }

    const url = `${FASTAPI_BASE_URL}/api/v1/risk/location?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}`;

    const response = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      const detail = await response.text().catch(() => "");
      if (response.status === 404) {
        return NextResponse.json(
          { risk_category: "Unknown", safety_score: 0, state, district, message: "Location not found in risk database", is_fallback: true },
          { status: 200 }
        );
      }
      return NextResponse.json(
        { status: "error", message: `Upstream error: ${response.status}${detail ? ` — ${detail}` : ""}` },
        { status: response.status >= 500 ? 502 : response.status }
      );
    }

    const data = await response.json();
    const safetyScore = data.safety_score ?? 0;
    const riskScore = Math.round((1 - safetyScore / 100) * 10000) / 10000;
    return NextResponse.json({
      risk_category: data.risk_category ?? "Unknown",
      safety_score: safetyScore,
      risk_score: riskScore,
      state: data.state ?? state,
      district: data.district ?? district,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Internal server error";
    return NextResponse.json(
      { status: "error", message: `Risk service unavailable: ${message}` },
      { status: 503 }
    );
  }
}

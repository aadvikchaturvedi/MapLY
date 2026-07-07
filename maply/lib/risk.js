export async function getRisk(state, district) {
  const res = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state, district }),
  });

  const data = await res.json();

  if (!res.ok) {
    console.warn("Risk lookup failed for", state, district, data);
    return {
      risk_category: "Unknown",
      safety_score: 0,
      risk_score: 0,
      is_fallback: true,
    };
  }

  return data;
}

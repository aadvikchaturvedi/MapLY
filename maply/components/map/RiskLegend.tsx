"use client";

import { useStore } from "@/store/useStore";

const TIERS = [
  { label: "Low Risk", score: "< 0.3", color: "#10B981", bg: "bg-[#10B981]/20", text: "text-[#10B981]" },
  { label: "Moderate", score: "0.3 – 0.6", color: "#F59E0B", bg: "bg-[#F59E0B]/20", text: "text-[#F59E0B]" },
  { label: "High Risk", score: "> 0.6", color: "#EF4444", bg: "bg-[#EF4444]/20", text: "text-[#EF4444]" },
];

export default function RiskLegend() {
  const globalRiskTier = useStore((s) => s.globalRiskTier);
  const currentRouteSegments = useStore((s) => s.currentRouteSegments);

  return (
    <div className="space-y-3 bg-card/60 backdrop-blur-sm rounded-xl border border-border/50 p-4 shadow-lg">
      <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Risk Legend</h4>
      <div className="space-y-2">
        {TIERS.map((tier) => (
          <div key={tier.label} className="flex items-center gap-2">
            <div
              className="h-3 w-3 rounded-full flex-shrink-0"
              style={{ backgroundColor: tier.color, boxShadow: `0 0 8px ${tier.color}80` }}
            />
            <span className="text-sm text-foreground flex-1">{tier.label}</span>
            <span className="text-xs text-muted-foreground">{tier.score}</span>
          </div>
        ))}
      </div>
      {currentRouteSegments.length > 0 && (
        <div className="pt-2 border-t border-border/40">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Global Tier</span>
            <span
              className={`font-bold px-2 py-0.5 rounded-full ${
                globalRiskTier === "low"
                  ? "bg-[#10B981]/20 text-[#10B981]"
                  : globalRiskTier === "moderate"
                  ? "bg-[#F59E0B]/20 text-[#F59E0B]"
                  : "bg-[#EF4444]/20 text-[#EF4444]"
              }`}
            >
              {globalRiskTier.toUpperCase()}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

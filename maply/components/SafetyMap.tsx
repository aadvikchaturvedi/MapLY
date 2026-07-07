"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { Search, Navigation, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useStore } from "@/store/useStore";
import { useLocation } from "@/hooks/useLocation";
import { getLatLng } from "@/lib/forwardGeocode";
import { getRoute } from "@/lib/routing";
import { apiPost } from "@/lib/api";
import { interpolateRoute } from "@/lib/geo";
import type { RouteSegment } from "@/types";

const MapContainer = dynamic(
  () => import("@/components/map/MapContainer"),
  { ssr: false, loading: () => <div className="h-full w-full bg-slate-900 animate-pulse rounded-3xl" /> }
);

function riskToCategory(riskScore: number): string {
  if (riskScore < 0.3) return "Low Risk";
  if (riskScore <= 0.6) return "Moderate Risk";
  return "High Risk";
}

export function SafetyMap() {
  const { location: userLoc } = useLocation();
  const setDestination = useStore((s) => s.setDestination);
  const setRouteSegments = useStore((s) => s.setRouteSegments);
  const destinationLocation = useStore((s) => s.destinationLocation);
  const currentRouteSegments = useStore((s) => s.currentRouteSegments);

  const globalRiskTier = useStore((s) => s.globalRiskTier);

  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [segments, setSegments] = useState<Array<{ risk: string; risk_score: number; path: Array<[number, number]> }>>([]);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim() || !userLoc) return;
    setLoading(true);
    setError(null);
    try {
      const dest = await getLatLng(searchQuery);
      setDestination({ lat: dest.lat, lng: dest.lng, name: searchQuery });

      const rawCoords = await getRoute(
        { lat: userLoc.lat, lng: userLoc.lng },
        { lat: dest.lat, lng: dest.lng }
      );

      const interpCoords = interpolateRoute(
        rawCoords.map((c: [number, number]) => ({ lat: c[0], lng: c[1] })),
        200
      );

      let routeSegments: Array<{ risk: string; risk_score: number; path: Array<[number, number]> }> = [];
      const batchSize = 50;
      for (let i = 0; i < interpCoords.length; i += batchSize) {
        const batch = interpCoords.slice(i, i + batchSize);
        const coordsPayload = batch.map((p) => [p.lat, p.lng]);
        try {
          const riskResp: { segments: RouteSegment[]; total: number } = await apiPost(
            "/api/v1/risk/route",
            { coordinates: coordsPayload }
          );
          if (riskResp.segments) {
            for (let j = 0; j < riskResp.segments.length - 1; j++) {
              const s = riskResp.segments[j];
              routeSegments.push({
                risk: riskToCategory(s.risk_score),
                risk_score: s.risk_score,
                path: [[s.lat, s.lng], [riskResp.segments[j + 1].lat, riskResp.segments[j + 1].lng]],
              });
            }
          }
        } catch {
          const fallback = batch.map((p) => ({
            risk: "Low Risk",
            risk_score: 0,
            path: [[p.lat, p.lng] as [number, number]],
          }));
          routeSegments.push(...fallback);
        }
      }

      const storeSegments: RouteSegment[] = routeSegments.map((s) => ({
        lat: s.path[0][0],
        lng: s.path[0][1],
        risk_score: s.risk_score,
        risk_category: s.risk_score < 0.3 ? "low" : s.risk_score <= 0.6 ? "moderate" : "high",
      }));
      setRouteSegments(storeSegments);
      setSegments(routeSegments);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to calculate route");
    } finally {
      setLoading(false);
    }
  }, [searchQuery, userLoc, setDestination, setRouteSegments]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch();
  }, [handleSearch]);

  const mapSegments = useMemo(() => segments, [segments]);

  return (
    <section id="map" className="relative py-24 overflow-hidden bg-background">
      <div
        className="absolute inset-0 z-0 opacity-[0.08] dark:opacity-[0.12]"
        style={{
          backgroundImage: `linear-gradient(to right, currentColor 1px, transparent 1px), linear-gradient(to bottom, currentColor 1px, transparent 1px)`,
          backgroundSize: "40px 40px",
        }}
      />
      <div className="absolute top-1/4 -right-20 w-[500px] h-[500px] bg-red-600/30 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 -left-20 w-[500px] h-[500px] bg-destructive/30 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-red-900/5 pointer-events-none" />

      <div className="container relative z-10 px-4 md:px-6 mx-auto">
        <div className="flex flex-col items-center text-center mb-8 space-y-4 max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-block rounded-full bg-destructive/10 px-4 py-1.5 text-sm text-destructive font-semibold border border-destructive/20 backdrop-blur-sm"
          >
            Live Risk Data
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl font-bold font-display tracking-tight sm:text-4xl"
          >
            Real-time Threat Analysis
          </motion.h2>
        </div>

        <div className="grid lg:grid-cols-5 gap-8 items-start">
          <div className="lg:col-span-3 relative h-[550px] w-full bg-slate-900 rounded-3xl overflow-hidden shadow-2xl border border-white/5">
            <div className="absolute top-4 left-4 right-4 z-[1000]">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    ref={inputRef}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Search destination..."
                    className="h-12 pl-10 pr-4 bg-background/90 backdrop-blur-md border-border/50 rounded-xl text-foreground placeholder:text-muted-foreground shadow-lg"
                  />
                </div>
                <Button
                  onClick={handleSearch}
                  disabled={loading || !searchQuery.trim()}
                  className="h-12 px-5 rounded-xl bg-primary hover:bg-primary/90 shadow-lg"
                >
                  {loading ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Navigation className="h-5 w-5" />
                  )}
                </Button>
              </div>
              {error && (
                <div className="mt-2 px-4 py-2 bg-destructive/20 backdrop-blur-md border border-destructive/30 rounded-lg text-sm text-destructive">
                  {error}
                </div>
              )}
            </div>

            <MapContainer segments={mapSegments} userLocation={userLoc} destination={destinationLocation} />

            {userLoc && (
              <div className="absolute bottom-4 left-4 bg-background/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-border/50 text-xs text-muted-foreground shadow-lg">
                {userLoc.lat.toFixed(4)}, {userLoc.lng.toFixed(4)}
              </div>
            )}
          </div>

          <div className="lg:col-span-2 space-y-6 flex flex-col">
            <div className="space-y-4 bg-card/50 backdrop-blur-sm rounded-2xl border border-border/50 p-6">
              <h4 className="font-semibold text-foreground text-lg">Route Risk Legend</h4>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="mt-1 h-3 w-3 rounded-full bg-[#10B981] shadow-[0_0_10px_rgba(16,185,129,0.5)] flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-foreground text-sm">Low Risk (Score &lt; 0.3)</h4>
                    <p className="text-xs text-muted-foreground">Well lit, crowded, active security presence.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-1 h-3 w-3 rounded-full bg-[#F59E0B] shadow-[0_0_10px_rgba(245,158,11,0.5)] flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-foreground text-sm">Moderate Risk (Score 0.3–0.6)</h4>
                    <p className="text-xs text-muted-foreground">Moderate lighting, fewer people, previous minor incidents.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-1 h-3 w-3 rounded-full bg-[#EF4444] shadow-[0_0_10px_rgba(239,68,68,0.5)] flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-foreground text-sm">High Risk (Score &gt; 0.6)</h4>
                    <p className="text-xs text-muted-foreground">Isolated, poor lighting, history of serious reports.</p>
                  </div>
                </div>
              </div>
            </div>

            {currentRouteSegments.length > 0 && (
              <div className="space-y-3 bg-card/50 backdrop-blur-sm rounded-2xl border border-border/50 p-6">
                <h4 className="font-semibold text-foreground">Route Summary</h4>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Global Risk Tier</span>
                  <span
                    className={`font-bold px-2 py-0.5 rounded-full text-xs ${
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
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Segments Analyzed</span>
                  <span className="font-bold">{currentRouteSegments.length}</span>
                </div>
              </div>
            )}

            <Button variant="outline" className="border-destructive/20 hover:bg-destructive/5">
              View Methodology
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}

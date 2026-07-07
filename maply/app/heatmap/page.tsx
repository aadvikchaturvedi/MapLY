"use client";

import { Nav } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Thermometer } from "lucide-react";

export default function HeatmapPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Nav />
      <main className="flex-1 pt-32 pb-20 container max-w-6xl mx-auto px-4">
        <div className="text-center space-y-4 mb-8">
          <h1 className="text-4xl font-bold font-display tracking-tight">Safety Heatmap</h1>
          <p className="text-muted-foreground text-lg">Crime density and risk visualization across cities</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/40 dark:bg-white/5 backdrop-blur-xl shadow-2xl p-8">
          <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
            <Thermometer className="h-12 w-12 mb-4 opacity-50" />
            <p className="text-lg font-medium">Heatmap data loading...</p>
            <p className="text-sm mt-2">Color-coded zones show relative safety levels across your route.</p>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

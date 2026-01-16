"use client";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

export function SafetyMap() {
  return (
    <section id="map" className="relative py-24 overflow-hidden bg-background">
      {/* Sophisticated Grid Background */}
      <div 
        className="absolute inset-0 z-0 opacity-[0.08] dark:opacity-[0.12]"
        style={{
          backgroundImage: `linear-gradient(to right, currentColor 1px, transparent 1px), linear-gradient(to bottom, currentColor 1px, transparent 1px)`,
          backgroundSize: '40px 40px'
        }}
      />
      
      {/* Deep Red Blurs */}
      <div className="absolute top-1/4 -right-20 w-[500px] h-[500px] bg-red-600/30 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 -left-20 w-[500px] h-[500px] bg-destructive/30 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-red-900/5 pointer-events-none" />

      <div className="container relative z-10 px-4 md:px-6 mx-auto">
        <div className="flex flex-col items-center text-center mb-16 space-y-4 max-w-3xl mx-auto">
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
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-muted-foreground text-lg"
          >
            Our proprietary algorithm combines official crime statistics, verified user reports, street lighting data, and store operating hours to calculate a dynamic safety score for every street.
          </motion.p>
        </div>

        <div className="grid lg:grid-cols-5 gap-12 items-center">
          <div className="lg:col-span-2 space-y-8 flex flex-col items-center lg:items-start text-center lg:text-left">
            <div className="space-y-6 w-full max-w-md">
              <div className="flex items-start gap-4 justify-center lg:justify-start">
                <div className="mt-1 h-3 w-3 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)] flex-shrink-0"></div>
                <div>
                  <h4 className="font-semibold text-foreground">Safe Zones (Score 8-10)</h4>
                  <p className="text-sm text-muted-foreground">Well lit, crowded, active security presence.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 justify-center lg:justify-start">
                <div className="mt-1 h-3 w-3 rounded-full bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.5)] flex-shrink-0"></div>
                <div>
                  <h4 className="font-semibold text-foreground">Caution Zones (Score 4-7)</h4>
                  <p className="text-sm text-muted-foreground">Moderate lighting, fewer people, previous minor incidents.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 justify-center lg:justify-start">
                <div className="mt-1 h-3 w-3 rounded-full bg-destructive shadow-[0_0_10px_rgba(239,68,68,0.5)] flex-shrink-0"></div>
                <div>
                  <h4 className="font-semibold text-foreground">High Risk Zones (Score 1-3)</h4>
                  <p className="text-sm text-muted-foreground">Isolated, poor lighting, history of serious reports.</p>
                </div>
              </div>
            </div>

            <Button variant="outline" className="mt-4 border-destructive/20 hover:bg-destructive/5">View Methodology</Button>
          </div>

          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="lg:col-span-3 relative h-[500px] w-full bg-slate-900 rounded-3xl overflow-hidden shadow-2xl border border-white/5"
          >
            {/* Mock Map UI */}
            <div className="absolute inset-0 opacity-40" 
                 style={{ 
                   backgroundImage: 'radial-gradient(circle at 50% 50%, #334155 1px, transparent 1px)',
                   backgroundSize: '20px 20px'
                 }}>
            </div>
            
            {/* Map Roads - Abstract */}
            <svg className="absolute inset-0 h-full w-full" style={{ filter: 'drop-shadow(0 0 4px rgba(0,0,0,0.5))' }}>
              <path d="M100 0 V500" stroke="#1e293b" strokeWidth="8" fill="none" />
              <path d="M300 0 V500" stroke="#1e293b" strokeWidth="8" fill="none" />
              <path d="M500 0 V500" stroke="#1e293b" strokeWidth="8" fill="none" />
              <path d="M0 150 H800" stroke="#1e293b" strokeWidth="8" fill="none" />
              <path d="M0 350 H800" stroke="#1e293b" strokeWidth="8" fill="none" />
              
              {/* Safe Route */}
              <motion.path 
                d="M100 500 V350 H300 V150 H500 V0" 
                stroke="#10b981" 
                strokeWidth="4" 
                fill="none"
                initial={{ pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                transition={{ duration: 2, ease: "easeInOut" }}
              />
            </svg>

            {/* Heatmap Blobs */}
            <motion.div 
              animate={{ opacity: [0.3, 0.5, 0.3] }}
              transition={{ duration: 4, repeat: Infinity }}
              className="absolute top-[20%] right-[20%] w-32 h-32 bg-green-500/20 rounded-full blur-2xl"
            />
             <motion.div 
              animate={{ opacity: [0.3, 0.6, 0.3] }}
              transition={{ duration: 3, repeat: Infinity }}
              className="absolute bottom-[20%] left-[20%] w-40 h-40 bg-orange-500/20 rounded-full blur-2xl"
            />
            <motion.div 
              animate={{ opacity: [0.4, 0.7, 0.4] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute top-[10%] left-[10%] w-24 h-24 bg-red-600/30 rounded-full blur-xl"
            />

            {/* UI Overlay */}
            <div className="absolute top-4 left-4 bg-background/90 backdrop-blur px-4 py-2 rounded-lg border border-border shadow-lg">
              <span className="text-xs font-mono text-muted-foreground">LIVE SAFETY INDEX</span>
              <div className="text-2xl font-bold font-display text-primary">94/100</div>
            </div>

            {/* User Location */}
             <motion.div 
              className="absolute top-[70%] left-[37.5%] w-4 h-4 bg-blue-500 border-2 border-white rounded-full shadow-lg z-10"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <div className="absolute inset-0 bg-blue-500 rounded-full animate-ping opacity-75"></div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
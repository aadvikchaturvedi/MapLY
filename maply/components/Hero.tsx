"use client";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-background pt-24 md:pt-32 lg:pt-40 pb-16 min-h-[85vh] flex items-center">
      {/* Deep Purple Radial Gradient Background */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
        <div 
          className="absolute inset-0 opacity-20 dark:opacity-40"
          style={{
            background: `radial-gradient(circle at 50% 50%, 
              hsl(270, 70%, 40%) 0%, 
              hsl(270, 70%, 30%) 20%, 
              hsl(270, 70%, 20%) 40%, 
              transparent 70%)`
          }}
        />
      </div>

      {/* Authentic Street Network Background */}
      <div className="absolute inset-0 z-0 opacity-60 dark:opacity-80 pointer-events-none overflow-hidden">
        <svg className="h-full w-full" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <filter id="red-glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feFlood floodColor="#ef4444" floodOpacity="0.4" result="color" />
              <feComposite in="color" in2="blur" operator="in" result="glow" />
              <feMerge>
                <feMergeNode in="glow" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          
          {/* Subtle Building Blocks */}
          <g fill="currentColor" className="text-muted/50">
            <rect x="50" y="50" width="80" height="120" rx="4" />
            <rect x="180" y="40" width="100" height="80" rx="4" />
            <rect x="50" y="220" width="120" height="100" rx="4" />
            <rect x="350" y="60" width="90" height="150" rx="4" />
            <rect x="550" y="80" width="150" height="90" rx="4" />
            <rect x="750" y="50" width="120" height="120" rx="4" />
            <rect x="40" y="450" width="140" height="110" rx="4" />
            <rect x="220" y="480" width="90" height="90" rx="4" />
            <rect x="600" y="420" width="110" height="130" rx="4" />
            <rect x="800" y="450" width="100" height="100" rx="4" />
          </g>

          {/* Grid Network (Horizontal/Vertical) */}
          <g stroke="currentColor" strokeWidth="4" className="text-muted/80">
            <path d="M0,200 L1000,200 M0,400 L1000,400 M0,600 L1000,600 M0,800 L1000,800" />
            <path d="M200,0 L200,1000 M400,0 L400,1000 M600,0 L600,1000 M800,0 L800,1000" />
          </g>

          {/* Additional Static Paths */}
          <g stroke="currentColor" strokeWidth="3" className="text-muted/60" fill="none">
            <path d="M100,0 V1000" />
            <path d="M300,0 V1000" />
            <path d="M500,0 V1000" />
            <path d="M700,0 V1000" />
            <path d="M900,0 V1000" />
            <path d="M0,100 H1000" />
            <path d="M0,300 H1000" />
            <path d="M0,500 H1000" />
            <path d="M0,700 H1000" />
            <path d="M0,900 H1000" />
          </g>

          {/* Diagonal Streets */}
          <g stroke="currentColor" strokeWidth="3" className="text-muted/70">
            <path d="M0,0 L1000,1000 M1000,0 L0,1000" />
            <path d="M200,0 L600,400 M0,400 L400,800" />
            <path d="M800,0 L400,400 M1000,600 L600,1000" />
          </g>

          {/* Curved Highway */}
          <path d="M0,100 C200,100 300,300 500,300 C700,300 800,100 1000,100" stroke="currentColor" strokeWidth="8" fill="none" className="text-muted/40" />

          {/* RE-POSITIONED UN-SAFE Path (Centralized for visibility) */}
          <path 
            d="M600,600 H800 V800 H1000" 
            stroke="#ef4444" 
            strokeWidth="10" 
            fill="none"
            filter="url(#red-glow)"
            className="opacity-60"
          />
          <text x="610" y="590" fill="#ef4444" className="text-[14px] font-bold uppercase tracking-widest opacity-80 drop-shadow-md">High Risk Zone</text>

          {/* Safe Route 1 (Original Direction) */}
          <motion.path 
            d="M200,1000 L200,600 L400,600 L400,400 L600,400 L600,200 L800,200" 
            stroke="#10b981" 
            strokeWidth="8" 
            strokeDasharray="15,12"
            fill="none"
            filter="url(#glow)"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 4, ease: "easeInOut", repeat: Infinity, repeatDelay: 1 }}
          />

          {/* Safe Route 2 (New Direction) */}
          <motion.path 
            d="M1000,400 H800 V600 H600 V800 H400 V1000" 
            stroke="#06b6d4" 
            strokeWidth="8" 
            strokeDasharray="15,12"
            fill="none"
            filter="url(#glow)"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 5, ease: "easeInOut", repeat: Infinity, repeatDelay: 1.5 }}
          />

          {/* Intersection Nodes */}
          <g fill="#10b981" className="opacity-90">
            <circle cx="200" cy="600" r="6" />
            <circle cx="400" cy="600" r="6" />
            <circle cx="400" cy="400" r="6" />
            <circle cx="600" cy="400" r="6" />
            <circle cx="600" cy="200" r="6" />
          </g>

          {/* Location Markers */}
          <motion.g
            animate={{ y: [0, -5, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <circle cx="800" cy="200" r="10" fill="#06b6d4" filter="url(#glow)" />
            <circle cx="800" cy="200" r="20" stroke="#06b6d4" strokeWidth="4" fill="none" className="opacity-50" />
          </motion.g>
        </svg>
      </div>

      <div className="container relative z-10 px-4 md:px-6 ml-0 md:ml-12 lg:ml-20">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-8 items-center">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex flex-col justify-center space-y-8"
          >
            <div className="space-y-4">
              <div className="inline-flex items-center rounded-full border border-accent/20 bg-accent/10 px-3 py-1 text-sm font-medium text-accent backdrop-blur-sm">
                <span className="flex h-2 w-2 rounded-full bg-accent mr-2 animate-pulse"></span>
                Now Live in Mumbai & Delhi
              </div>
              <h1 className="font-display text-4xl font-bold tracking-tighter sm:text-5xl xl:text-7xl/none text-primary">
                Navigate your world with <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-destructive">confidence.</span>
              </h1>
              <p className="max-w-[600px] text-muted-foreground md:text-xl leading-relaxed">
                The first intelligent safety map that prioritizes your wellbeing over distance. 
                Real-time risk data, lighting scores, and community-verified safe zones.
              </p>
            </div>
            <div className="flex flex-col gap-4 sm:flex-row">
              <Link href="/plan">
                <Button size="lg" className="h-12 px-8 text-lg gap-2 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20">
                  Find Safe Route <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="h-12 px-8 text-lg border-primary/20 hover:bg-primary/5 backdrop-blur-sm">
                Explore Heatmap
              </Button>
            </div>
            
            <div className="flex items-center gap-8 pt-4">
              <div className="flex flex-col">
                <span className="text-3xl font-bold font-display text-primary">2.4M+</span>
                <span className="text-sm text-muted-foreground">Safe Routes</span>
              </div>
              <div className="h-10 w-px bg-border"></div>
              <div className="flex flex-col">
                <span className="text-3xl font-bold font-display text-primary">50k+</span>
                <span className="text-sm text-muted-foreground">Active Guardians</span>
              </div>
            </div>
          </motion.div>
          
          <div className="hidden lg:block relative" />
        </div>
      </div>
    </section>
  );
}
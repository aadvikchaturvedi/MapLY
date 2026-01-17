"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MapPin, Navigation, Clock, Ruler, Shield, ArrowLeft, Loader2, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Card, CardContent } from "@/components/ui/card";
import { Nav } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import Map from "@/components/map/MapContainer";
import { useToast } from "@/hooks/use-toast";
import { getLatLng } from "@/lib/forwardGeocode";
import { getRoute, simplifyRoute } from "@/lib/routing";
import { getDistrict } from "@/lib/geocode";
import { getRisk } from "@/lib/risk";

interface RouteSegment {
  path: [number, number][];
  risk: string;
}


export default function Planner() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    from: "",
    to: "",
    priority: "safety"
  });
 const [segments, setSegments] = useState<RouteSegment[]>([]);

  const [route, setRoute] = useState([]);

  const handlePlan = async () => {

  if (!formData.from || !formData.to) {
    toast({
      title: "Missing Information",
      description: "Please enter both departure and destination points.",
      variant: "destructive"
    });
    return;
  }

  try {
    setLoading(true);

    // 1️⃣ Convert user text → coordinates
    const start = await getLatLng(formData.from);
    const end   = await getLatLng(formData.to);

    // 2️⃣ Get route
    const rawCoords = await getRoute(start, end);
    const points = simplifyRoute(rawCoords);

    let segments = [];

    for (let i = 0; i < points.length - 1; i++) {

      const p1 = points[i];
      const p2 = points[i + 1];
      console.log("Processing segment:", p1, p2);
      const loc = await getDistrict(p1[0], p1[1]);
      const risk = await getRisk(loc.state, loc.district);

      segments.push({
        path: [p1, p2],
        risk: risk.risk_category
      });
    }

    setSegments(segments);
    setStep(2);

  } catch (err) {
    toast({
      title: "Error",
      description: "Unable to calculate route",
      variant: "destructive"
    });
  }

  setLoading(false);
};



  return (
    <div className="min-h-screen bg-background font-sans selection:bg-accent/20 relative flex flex-col">
      <div className="flex-grow relative overflow-hidden">
        <Nav />

        {/* Dynamic Multi-Color Grid Background */}
        <div 
          className="absolute inset-0 z-0 opacity-[0.15]"
          style={{
            backgroundImage: `linear-gradient(to right, #ef4444 1px, transparent 1px), linear-gradient(to bottom, #ef4444 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
            maskImage: 'linear-gradient(to right, black 33%, transparent 33%)',
            WebkitMaskImage: 'linear-gradient(to right, black 33%, transparent 33%)'
          }}
        />
        <div 
          className="absolute inset-0 z-0 opacity-[0.15]"
          style={{
            backgroundImage: `linear-gradient(to right, #ffffff 1px, transparent 1px), linear-gradient(to bottom, #ffffff 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
            maskImage: 'linear-gradient(to right, transparent 33%, black 33%, black 66%, transparent 66%)',
            WebkitMaskImage: 'linear-gradient(to right, transparent 33%, black 33%, black 66%, transparent 66%)'
          }}
        />
        <div 
          className="absolute inset-0 z-0 opacity-[0.15]"
          style={{
            backgroundImage: `linear-gradient(to right, #7c3aed 1px, transparent 1px), linear-gradient(to bottom, #7c3aed 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
            maskImage: 'linear-gradient(to right, transparent 66%, black 66%)',
            WebkitMaskImage: 'linear-gradient(to right, transparent 66%, black 66%)'
          }}
        />

        {/* Ambient Glows */}
        <div className="absolute top-1/4 -left-20 w-[500px] h-[500px] bg-red-900/20 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-white/5 rounded-full blur-[140px] pointer-events-none" />
        <div className="absolute bottom-1/4 -right-20 w-[500px] h-[500px] bg-purple-900/20 rounded-full blur-[120px] pointer-events-none" />
        
        <main className="pt-32 pb-20 container max-w-4xl mx-auto px-4 relative z-10">
        <AnimatePresence mode="wait">
          {step === 1 ? (
            <motion.div
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-8"
            >
              <div className="text-center space-y-4">
                <h1 className="text-4xl font-bold font-display tracking-tight">Plan Your Safe Journey</h1>
                <p className="text-muted-foreground text-lg">Enter your details and let our AI find the most secure path for you.</p>
              </div>

              <Card className="border-white/10 bg-white/40 dark:bg-white/5 backdrop-blur-xl shadow-2xl p-6 md:p-8">
                <CardContent className="space-y-8 pt-6">
                  <div className="grid gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="from" className="text-sm font-semibold flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-primary" /> Departure Point
                      </Label>
                      <Input 
                        id="from" 
                        placeholder="e.g. Connaught Place, Delhi" 
                        className="h-12 bg-background/50 rounded-xl"
                        value={formData.from}
                        onChange={(e) => setFormData({ ...formData, from: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="to" className="text-sm font-semibold flex items-center gap-2">
                        <Navigation className="h-4 w-4 text-accent" /> Destination Point
                      </Label>
                      <Input 
                        id="to" 
                        placeholder="e.g. Cyber City, Gurgaon" 
                        className="h-12 bg-background/50 rounded-xl"
                        value={formData.to}
                        onChange={(e) => setFormData({ ...formData, to: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Label className="text-sm font-semibold">Route Priority</Label>
                    <RadioGroup 
                      defaultValue="safety" 
                      className="grid grid-cols-1 md:grid-cols-3 gap-4"
                      onValueChange={(val) => setFormData({ ...formData, priority: val })}
                    >
                      <div className="relative">
                        <RadioGroupItem value="safety" id="safety" className="peer sr-only" />
                        <Label
                          htmlFor="safety"
                          className="flex flex-col items-center justify-between rounded-xl border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer transition-all"
                        >
                          <Shield className="mb-3 h-6 w-6 text-primary" />
                          <span className="font-bold">Safest</span>
                          <span className="text-[10px] text-muted-foreground uppercase mt-1">Priority: Safety</span>
                        </Label>
                      </div>
                      <div className="relative">
                        <RadioGroupItem value="fastest" id="fastest" className="peer sr-only" />
                        <Label
                          htmlFor="fastest"
                          className="flex flex-col items-center justify-between rounded-xl border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer transition-all"
                        >
                          <Clock className="mb-3 h-6 w-6 text-blue-500" />
                          <span className="font-bold">Fastest</span>
                          <span className="text-[10px] text-muted-foreground uppercase mt-1">Priority: Time</span>
                        </Label>
                      </div>
                      <div className="relative">
                        <RadioGroupItem value="balanced" id="balanced" className="peer sr-only" />
                        <Label
                          htmlFor="balanced"
                          className="flex flex-col items-center justify-between rounded-xl border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer transition-all"
                        >
                          <Ruler className="mb-3 h-6 w-6 text-orange-500" />
                          <span className="font-bold">Balanced</span>
                          <span className="text-[10px] text-muted-foreground uppercase mt-1">Safest + Shortest</span>
                        </Label>
                      </div>
                    </RadioGroup>
                  </div>

                  <Button 
                    className="w-full h-14 text-lg font-bold rounded-xl bg-primary hover:bg-primary/90 shadow-xl shadow-primary/20"
                    onClick={handlePlan}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        Analyzing Safe Zones...
                      </>
                    ) : (
                      "Calculate Safest Path"
                    )}
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          ) : (
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-8"
            >
              <div className="flex items-center justify-between">
                <Button variant="ghost" onClick={() => setStep(1)} className="gap-2">
                  <ArrowLeft className="h-4 w-4" /> Edit Route
                </Button>
                <div className="flex items-center gap-2 text-secondary font-bold bg-secondary/10 px-4 py-2 rounded-full border border-secondary/20">
                  <CheckCircle2 className="h-5 w-5" /> AI Verified Path
                </div>
              </div>

              <div className="grid gap-6 md:grid-cols-3">
                <Card className="md:col-span-2 relative h-[500px] bg-slate-900 rounded-3xl overflow-hidden border border-white/10 shadow-2xl">
                   <Map segments={segments} />
                </Card>

                <div className="space-y-4">
                  <h3 className="font-bold text-xl">Route Insights</h3>
                  <div className="space-y-4">
                    <div className="p-4 rounded-2xl bg-muted/30 border border-border space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Safety Score</span>
                        <span className="text-secondary font-bold">9.8/10</span>
                      </div>
                      <div className="h-2 w-full bg-secondary/10 rounded-full overflow-hidden">
                        <div className="h-full bg-secondary w-[98%]" />
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <p className="text-xs font-bold text-muted-foreground uppercase">Key Features along this path:</p>
                      {[
                        "Continuous Street Lighting",
                        "High Foot Traffic Area",
                        "3 Verified Police Outposts",
                        "Open Pharmacies nearby"
                      ].map((feature, i) => (
                        <div key={i} className="flex items-center gap-3 text-sm">
                          <CheckCircle2 className="h-4 w-4 text-secondary" />
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>

                    <Button className="w-full h-12 rounded-xl bg-accent hover:bg-accent/90">
                      Start Navigation
                    </Button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
    <Footer />
  </div>
  );
}

function setCrimeZones(crimeZones: any) {
    throw new Error("Function not implemented.");
}
function setRoute(safeRoute: any) {
    throw new Error("Function not implemented.");
}


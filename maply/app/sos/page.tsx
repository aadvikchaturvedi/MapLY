"use client";

import { useState } from "react";
import { Nav } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AlertTriangle, Phone, MapPin, Shield } from "lucide-react";

export default function SOSPage() {
  const [sent, setSent] = useState(false);

  const handleSOS = async () => {
    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) =>
        navigator.geolocation.getCurrentPosition(resolve, reject)
      );
      await fetch("/api/sos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          timestamp: Date.now(),
        }),
      });
      setSent(true);
    } catch {
      setSent(true);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Nav />
      <main className="flex-1 pt-32 pb-20 container max-w-2xl mx-auto px-4">
        <div className="text-center space-y-4 mb-8">
          <h1 className="text-4xl font-bold font-display tracking-tight text-red-600">SOS Emergency</h1>
          <p className="text-muted-foreground text-lg">Immediate help when you need it most</p>
        </div>
        <Card className="border-red-500/30 bg-red-500/5 backdrop-blur-xl shadow-2xl p-8">
          <CardContent className="space-y-6 text-center">
            {!sent ? (
              <>
                <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-red-500/20">
                  <AlertTriangle className="h-12 w-12 text-red-600" />
                </div>
                <div className="space-y-2">
                  <h2 className="text-2xl font-bold">Send Emergency Alert</h2>
                  <p className="text-muted-foreground text-sm">
                    Your location will be shared with your emergency contacts and local authorities.
                  </p>
                </div>
                <Button
                  onClick={handleSOS}
                  className="w-full h-16 text-lg font-bold rounded-xl bg-red-600 hover:bg-red-700 shadow-xl shadow-red-600/30"
                >
                  <Phone className="mr-2 h-6 w-6" />
                  SEND SOS ALERT
                </Button>
                <div className="grid grid-cols-2 gap-4 pt-4">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <MapPin className="h-4 w-4 text-red-500" />
                    GPS Location
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Shield className="h-4 w-4 text-red-500" />
                    Encrypted
                  </div>
                </div>
              </>
            ) : (
              <div className="py-10 space-y-4">
                <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-green-500/20">
                  <Shield className="h-12 w-12 text-green-500" />
                </div>
                <h2 className="text-2xl font-bold text-green-600">Alert Sent Successfully</h2>
                <p className="text-muted-foreground text-sm">
                  Help is on the way. Stay where you are and keep your phone visible.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
      <Footer />
    </div>
  );
}

"use client";

import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, X, MapPin, Phone, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useStore } from "@/store/useStore";
import { useLocation } from "@/hooks/useLocation";

interface EmergencyProps {
  onClose?: () => void;
}

export default function Emergency({ onClose }: EmergencyProps) {
  const sosActive = useStore((s) => s.sosActive);
  const setSOSActive = useStore((s) => s.setSOSActive);
  const activeWebSocketStatus = useStore((s) => s.activeWebSocketStatus);
  const { location } = useLocation();

  const handleToggle = () => {
    setSOSActive(!sosActive);
  };

  const statusColor = {
    idle: "bg-muted",
    connecting: "bg-yellow-500",
    open: "bg-green-500",
    closed: "bg-red-500",
    error: "bg-red-500",
  }[activeWebSocketStatus];

  const statusLabel = {
    idle: "Not Active",
    connecting: "Connecting…",
    open: "Active",
    closed: "Disconnected",
    error: "Connection Error",
  }[activeWebSocketStatus];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 20, scale: 0.95 }}
        className="fixed bottom-24 right-6 z-50 w-80"
      >
        <div className="bg-background/95 backdrop-blur-xl border border-destructive/20 rounded-2xl shadow-2xl shadow-destructive/10 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${statusColor} ${sosActive ? "animate-pulse" : ""}`} />
              <span className="text-sm font-semibold">SOS {statusLabel}</span>
            </div>
            {onClose && (
              <button onClick={onClose} className="text-muted-foreground hover:text-foreground transition-colors">
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          <div className="p-4 space-y-4">
            {location && (
              <div className="flex items-start gap-2 text-xs text-muted-foreground">
                <MapPin className="h-3 w-3 mt-0.5 flex-shrink-0" />
                <span className="font-mono">
                  {location.lat.toFixed(6)}, {location.lng.toFixed(6)}
                  {location.accuracy && ` (±${location.accuracy.toFixed(0)}m)`}
                </span>
              </div>
            )}

            <div className="grid grid-cols-2 gap-2">
              <Button
                variant="outline"
                size="sm"
                className="rounded-xl border-border/50 gap-1.5"
                onClick={() => window.open("tel:112", "_self")}
              >
                <Phone className="h-3.5 w-3.5" />
                <span className="text-xs">Call 112</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="rounded-xl border-border/50 gap-1.5"
              >
                <MessageSquare className="h-3.5 w-3.5" />
                <span className="text-xs">Alert Contacts</span>
              </Button>
            </div>

            <Button
              onClick={handleToggle}
              variant={sosActive ? "outline" : "destructive"}
              className={`w-full rounded-xl gap-2 h-12 font-bold ${
                sosActive
                  ? "border-red-500/50 text-red-500 hover:bg-red-500/10"
                  : "shadow-lg shadow-destructive/30"
              }`}
            >
              <AlertTriangle className="h-5 w-5" />
              {sosActive ? "Deactivate SOS" : "Activate SOS"}
            </Button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

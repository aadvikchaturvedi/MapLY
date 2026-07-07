"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle } from "lucide-react";
import { useStore } from "@/store/useStore";
import { useSOS } from "@/hooks/useSOS";
import Emergency from "@/components/sos/Emergency";

export function SOSButton() {
  const [showPanel, setShowPanel] = useState(false);
  const sosActive = useStore((s) => s.sosActive);
  const setSOSActive = useStore((s) => s.setSOSActive);
  const activeWebSocketStatus = useStore((s) => s.activeWebSocketStatus);

  // Wire the SOS connectivity hook — it activates/deactivates based on store state
  useSOS();

  const handlePress = () => {
    // Single tap toggles panel; long-press behavior could be added
    if (sosActive) {
      setSOSActive(false);
      setShowPanel(false);
    } else {
      setShowPanel(!showPanel);
    }
  };

  const isConnected = activeWebSocketStatus === "open";
  const isError = activeWebSocketStatus === "error";

  return (
    <>
      <AnimatePresence>
        {showPanel && <Emergency onClose={() => setShowPanel(false)} />}
      </AnimatePresence>

      <motion.button
        onClick={handlePress}
        initial={{ scale: 0.9 }}
        animate={{
          scale: sosActive ? [1, 1.08, 1] : 1,
          rotate: sosActive ? [0, -5, 5, -5, 0] : 0,
        }}
        transition={{
          scale: sosActive
            ? { repeat: Infinity, duration: 1.5, ease: "easeInOut" }
            : { type: "spring", stiffness: 400, damping: 17 },
          rotate: sosActive
            ? { repeat: Infinity, duration: 0.5 }
            : { duration: 0.3 },
        }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className={`fixed bottom-6 right-6 z-50 flex h-16 w-16 items-center justify-center rounded-full shadow-lg ring-4 transition-all md:h-20 md:w-20 ${
          sosActive
            ? "bg-red-600 text-white ring-red-500/50 shadow-red-500/40"
            : "bg-destructive text-destructive-foreground ring-destructive/20 shadow-destructive/40"
        }`}
        aria-label={sosActive ? "SOS Active" : "Trigger SOS"}
      >
        <div className="flex flex-col items-center justify-center">
          <AlertTriangle className="h-8 w-8 md:h-10 md:w-10 fill-current" />
          <span className="text-[10px] font-bold uppercase tracking-wider md:text-xs">
            {sosActive ? "ACTIVE" : "SOS"}
          </span>
        </div>

        {isConnected && sosActive && (
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-500 opacity-30" />
        )}
        {isError && (
          <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-yellow-500 border-2 border-background" />
        )}
        {!sosActive && (
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-destructive opacity-20" />
        )}
      </motion.button>
    </>
  );
}

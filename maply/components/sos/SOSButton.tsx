"use client";
import { motion } from "framer-motion";
import { AlertTriangle } from "lucide-react";

export function SOSButton() {
  return (
    <motion.button
      initial={{ scale: 0.9 }}
      animate={{ scale: 1 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{ 
        type: "spring", 
        stiffness: 400, 
        damping: 17,
        repeat: Infinity,
        repeatType: "reverse",
        duration: 2
      }}
      className="fixed bottom-6 right-6 z-50 flex h-16 w-16 items-center justify-center rounded-full bg-destructive text-destructive-foreground shadow-lg shadow-destructive/40 ring-4 ring-destructive/20 transition-all hover:shadow-xl hover:shadow-destructive/60 focus:outline-none focus:ring-4 focus:ring-destructive/50 md:h-20 md:w-20"
      aria-label="Trigger SOS"
    >
      <div className="flex flex-col items-center justify-center">
        <AlertTriangle className="h-8 w-8 md:h-10 md:w-10 fill-current" />
        <span className="text-[10px] font-bold uppercase tracking-wider md:text-xs">SOS</span>
      </div>
      
      {/* Pulse Effect */}
      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-destructive opacity-20"></span>
    </motion.button>
  );
}
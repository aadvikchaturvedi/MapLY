"use client";

import { useToast } from "@/hooks/use-toast";
import {
  ToastProps,
} from "@/components/ui/toast";

export function Toaster() {
  const { toasts, dismiss } = useToast();

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`rounded-xl border px-4 py-3 shadow-lg backdrop-blur-xl transition-all duration-300 ${
            t.open ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2 pointer-events-none"
          } ${
            t.variant === "destructive"
              ? "border-red-500/30 bg-red-500/10 text-red-600"
              : "border-white/20 bg-white/90 dark:bg-gray-900/90 text-foreground"
          }`}
          onClick={() => dismiss(t.id)}
        >
          {t.title && <p className="text-sm font-bold">{t.title}</p>}
          {t.description && <p className="text-xs mt-1 opacity-80">{t.description}</p>}
        </div>
      ))}
    </div>
  );
}

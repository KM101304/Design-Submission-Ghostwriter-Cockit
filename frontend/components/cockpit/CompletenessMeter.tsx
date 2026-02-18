import { motion } from "framer-motion";

import { toneColor } from "@/lib/cockpit";

export function CompletenessMeter({ value, status }: { value: number; status: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/20 p-3">
      <div className="flex items-center justify-between text-xs">
        <span className="text-[var(--muted)]">Completeness</span>
        <span className="text-[var(--text)]">{value}%</span>
      </div>
      <div className="mt-2 h-2.5 rounded-full bg-white/10">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(0, Math.min(100, value))}%` }}
          transition={{ duration: 0.5 }}
          className="h-2.5 rounded-full"
          style={{ background: toneColor(status) }}
        />
      </div>
    </div>
  );
}

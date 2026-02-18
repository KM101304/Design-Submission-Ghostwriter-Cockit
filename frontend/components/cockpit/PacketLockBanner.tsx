import { motion } from "framer-motion";
import { ShieldCheck, Sparkles } from "lucide-react";

export function PacketLockBanner({ locked }: { locked: boolean }) {
  if (!locked) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-[var(--ok)]/40 bg-[var(--ok)]/12 px-4 py-3 shadow-[0_0_45px_-20px_rgba(55,215,150,0.95)]"
    >
      <div className="flex items-center gap-3">
        <ShieldCheck className="h-5 w-5 text-[var(--ok)]" />
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-[var(--ok)]">Packet Locked</p>
          <p className="mt-1 text-sm text-[var(--text)]">Submission is bind-ready and fully structured.</p>
        </div>
        <Sparkles className="ml-auto h-4 w-4 text-[var(--ok)]" />
      </div>
    </motion.div>
  );
}

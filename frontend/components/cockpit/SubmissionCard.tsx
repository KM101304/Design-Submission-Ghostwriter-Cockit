import { motion } from "framer-motion";

import { SubmissionListItem } from "@/components/cockpit/types";
import { statusTone, submissionProgress, toneColor } from "@/lib/cockpit";

export function SubmissionCard({
  item,
  active,
  onClick,
}: {
  item: SubmissionListItem;
  active: boolean;
  onClick: () => void;
}) {
  const tone = statusTone(item.job_status);
  const dot = tone === "ok" ? "var(--ok)" : tone === "warn" ? "var(--warn)" : tone === "bad" ? "var(--bad)" : "var(--muted)";
  const pct = submissionProgress(item.job_status);

  return (
    <motion.button
      whileHover={{ y: -2 }}
      onClick={onClick}
      className={`w-full rounded-xl border p-3 text-left transition ${
        active ? "border-[var(--accent)]/60 bg-[var(--accent)]/10" : "border-white/10 bg-black/25 hover:border-white/25"
      }`}
    >
      <div className="flex items-start gap-2">
        <span className="mt-1 inline-block h-2.5 w-2.5 rounded-full" style={{ background: dot }} />
        <div className="min-w-0 flex-1">
          <p className="truncate text-[11px] text-[var(--muted)]">{item.submission_id}</p>
          <p className="mt-1 line-clamp-2 text-sm font-medium text-[var(--text)]">{item.filename}</p>
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between text-[11px] text-[var(--muted)]">
        <span>{item.job_status}</span>
        <span>{pct}%</span>
      </div>
      <div className="mt-1 h-1.5 rounded-full bg-white/10">
        <div className="h-1.5 rounded-full" style={{ width: `${pct}%`, background: toneColor(item.job_status.includes("processed") ? "Green" : item.job_status.includes("failed") ? "Red" : "Yellow") }} />
      </div>
    </motion.button>
  );
}

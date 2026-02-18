import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, Link2 } from "lucide-react";
import { useMemo, useState } from "react";

export function RiskField({
  label,
  value,
  confidence,
  citations,
}: {
  label: string;
  value: string;
  confidence?: number;
  citations?: Array<{ source_document: string; page: number | null; snippet: string | null }>;
}) {
  const [open, setOpen] = useState(false);

  const confidenceText = useMemo(() => {
    if (confidence == null) return "Confidence N/A";
    return `Confidence ${Math.round(confidence * 100)}%`;
  }, [confidence]);

  return (
    <div className="rounded-xl border border-white/10 bg-black/20 p-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[10px] uppercase tracking-[0.14em] text-[var(--muted)]">{label}</p>
          <p className="mt-1 text-sm font-medium text-[var(--text)]">{value}</p>
          <p className="mt-1 text-[10px] text-[var(--muted)]">{confidenceText}</p>
        </div>
        <button onClick={() => setOpen((v) => !v)} className="inline-flex items-center gap-1 rounded-md border border-white/15 px-2 py-1 text-[10px] text-[var(--muted)] hover:bg-white/8">
          <Link2 className="h-3 w-3" />
          Provenance
          <ChevronDown className={`h-3 w-3 transition ${open ? "rotate-180" : ""}`} />
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="mt-3 space-y-1 rounded-lg border border-white/10 bg-black/20 p-2 text-xs text-[var(--muted)]">
              {(citations ?? []).length === 0 && <p>No provenance found.</p>}
              {(citations ?? []).map((c, idx) => (
                <p key={`${c.source_document}-${idx}`}>
                  {c.source_document}
                  {c.page != null ? ` · p.${c.page}` : ""}
                  {c.snippet ? ` · ${c.snippet}` : ""}
                </p>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

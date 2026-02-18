import { AlertTriangle } from "lucide-react";

export function AIAlert({ items }: { items: string[] }) {
  if (items.length === 0) return null;

  return (
    <div className="rounded-xl border border-[var(--bad)]/35 bg-[var(--bad)]/12 p-3">
      <div className="flex items-center gap-2 text-[var(--bad)]">
        <AlertTriangle className="h-4 w-4" />
        <p className="text-[11px] uppercase tracking-[0.14em]">Contradiction Detected</p>
      </div>
      <ul className="mt-2 space-y-1 text-xs text-[var(--text)]">
        {items.map((item, idx) => (
          <li key={`${item}-${idx}`}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

import { Mail, Sparkles } from "lucide-react";

export function FollowUpPreview({
  lines,
  emailDraft,
  onCopy,
  copied,
}: {
  lines: string[];
  emailDraft: string;
  onCopy: () => void;
  copied: boolean;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/20 p-3">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-[var(--accent)]" />
        <p className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">AI Follow-Up Generator</p>
      </div>
      <ul className="mt-2 space-y-1 text-sm text-[var(--text)]">
        {lines.map((line, idx) => (
          <li key={`${line}-${idx}`}>{line}</li>
        ))}
      </ul>
      <button onClick={onCopy} className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-white/20 px-3 py-2 text-xs text-[var(--text)] transition hover:bg-white/8">
        <Mail className="h-3.5 w-3.5" />
        {copied ? "Copied Draft" : "Copy Email Draft"}
      </button>
      <pre className="mt-3 max-h-36 overflow-auto rounded-lg border border-white/10 bg-black/25 p-2 text-[11px] text-[var(--muted)]">
        {emailDraft}
      </pre>
    </div>
  );
}

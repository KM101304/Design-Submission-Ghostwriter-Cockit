const submissions = [
  { id: "SUB-1842", name: "Mason Fabrication LLC", status: "Quote-ready", score: 78 },
  { id: "SUB-1843", name: "Harbor Clinical Group", status: "Incomplete", score: 43 },
  { id: "SUB-1844", name: "Atlas Specialty Foods", status: "Bind-ready", score: 92 },
];

export default function CockpitPage() {
  return (
    <main className="min-h-screen p-6">
      <div className="mb-4 rounded-xl border border-white/10 bg-[var(--panel)]/80 px-4 py-3">
        <p className="text-xs uppercase tracking-widest text-[var(--muted)]">Packet State</p>
        <div className="mt-1 flex items-center justify-between">
          <h1 className="text-xl font-semibold">Submission Ghostwriter Cockpit</h1>
          <span className="rounded-full border border-[var(--warn)]/60 bg-[var(--warn)]/10 px-3 py-1 text-xs text-[var(--warn)]">
            Packet Unlocked
          </span>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[280px_1fr_340px]">
        <section className="rounded-xl border border-white/10 bg-[var(--panel)]/80 p-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">Submissions</h2>
          <div className="mt-3 space-y-2">
            {submissions.map((item) => (
              <article key={item.id} className="rounded-lg border border-white/10 bg-black/20 p-3">
                <p className="text-xs text-[var(--muted)]">{item.id}</p>
                <p className="text-sm font-medium">{item.name}</p>
                <p className="mt-2 text-xs text-[var(--muted)]">{item.status}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="rounded-xl border border-white/10 bg-[var(--panel)]/80 p-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">Risk Profile Summary</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <Tile label="Insured" value="Mason Fabrication LLC" />
            <Tile label="Entity Type" value="LLC" />
            <Tile label="Revenue" value="$5.2M" />
            <Tile label="Payroll" value="$1.8M" />
            <Tile label="Locations" value="3" />
            <Tile label="Lines" value="GL, WC, Auto" />
          </div>
        </section>

        <section className="rounded-xl border border-white/10 bg-[var(--panel)]/80 p-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">Completeness + Questions</h2>
          <ScoreBar label="GL" value={88} tone="ok" />
          <ScoreBar label="WC" value={74} tone="warn" />
          <ScoreBar label="Auto" value={52} tone="bad" />

          <div className="mt-4 rounded-lg border border-white/10 bg-black/20 p-3">
            <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Missing Fields</p>
            <ul className="mt-2 space-y-1 text-sm">
              <li>Driver schedule + MVR recency</li>
              <li>5-year loss runs confirmation</li>
              <li>WC class code breakout by location</li>
            </ul>
          </div>
        </section>
      </div>
    </main>
  );
}

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 p-3">
      <p className="text-xs uppercase tracking-wide text-[var(--muted)]">{label}</p>
      <p className="mt-1 text-sm font-medium">{value}</p>
    </div>
  );
}

function ScoreBar({ label, value, tone }: { label: string; value: number; tone: "ok" | "warn" | "bad" }) {
  const color = tone === "ok" ? "var(--ok)" : tone === "warn" ? "var(--warn)" : "var(--bad)";
  return (
    <div className="mt-3">
      <div className="mb-1 flex items-center justify-between text-xs">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-white/10">
        <div className="h-2 rounded-full" style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
  );
}

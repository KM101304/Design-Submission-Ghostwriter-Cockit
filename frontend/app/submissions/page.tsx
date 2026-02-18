import Link from "next/link";

const demoRows = [
  { id: "SUB-1024", insured: "Northline Plumbing LLC", status: "Quote Ready", completeness: "92%" },
  { id: "SUB-1023", insured: "Apex Electrical Services", status: "Needs Info", completeness: "68%" },
  { id: "SUB-1022", insured: "Summit Hotel Group", status: "Packet Locked", completeness: "100%" },
];

export default function SubmissionsPage() {
  return (
    <section>
      <div className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-md">
        <p className="text-xs uppercase tracking-[0.18em] text-white/60">Submissions</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">Submission Workspace</h1>
        <p className="mt-2 text-sm text-white/65">Review packet health and jump back into AI-guided resolution.</p>
      </div>

      <div className="mt-10 rounded-xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-md">
        <div className="grid gap-6">
          {demoRows.map((row) => (
            <div key={row.id} className="grid gap-4 rounded-xl border border-white/10 bg-black/20 p-4 md:grid-cols-[1.5fr_1fr_1fr_auto] md:items-center">
              <div>
                <p className="text-xs uppercase tracking-[0.12em] text-white/50">{row.id}</p>
                <p className="mt-1 text-base font-medium text-white">{row.insured}</p>
              </div>
              <p className="text-sm text-white/75">{row.status}</p>
              <p className="text-sm text-white/75">{row.completeness}</p>
              <Link href="/dashboard" className="rounded-lg border border-cyan-300/30 bg-cyan-300/10 px-4 py-2 text-sm text-cyan-100 transition hover:bg-cyan-300/20">
                Open Cockpit
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

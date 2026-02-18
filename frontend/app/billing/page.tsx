const plans = [
  { name: "Starter", price: "$299/mo", summary: "For small teams processing standard SMB packets." },
  { name: "Pro", price: "$599/mo", summary: "For brokerages running daily AI submission workflows.", highlighted: true },
  { name: "Brokerage", price: "$899/mo", summary: "For multi-seat operations with audit and usage controls." },
];

export default function BillingPage() {
  return (
    <section>
      <div className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-md">
        <p className="text-xs uppercase tracking-[0.18em] text-white/60">Billing</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">Plans Built for Brokerage Teams</h1>
        <p className="mt-2 text-sm text-white/65">Scale seats, AI runs, and audit retention with predictable monthly pricing.</p>
      </div>

      <div className="mt-10 grid gap-8 md:grid-cols-3">
        {plans.map((plan) => (
          <article
            key={plan.name}
            className={`rounded-xl border p-6 shadow-xl backdrop-blur-md ${
              plan.highlighted ? "border-cyan-300/45 bg-cyan-300/10" : "border-white/10 bg-white/5"
            }`}
          >
            <p className="text-sm uppercase tracking-[0.14em] text-white/65">{plan.name}</p>
            <p className="mt-4 text-3xl font-semibold text-white">{plan.price}</p>
            <p className="mt-3 text-sm text-white/75">{plan.summary}</p>
            <button className="mt-8 w-full rounded-lg bg-white/90 px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-white">
              Choose Plan
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}

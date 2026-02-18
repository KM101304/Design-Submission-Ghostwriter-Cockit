export default function AccountPage() {
  return (
    <section>
      <div className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-md">
        <p className="text-xs uppercase tracking-[0.18em] text-white/60">Account</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">Brokerage Account Settings</h1>
        <p className="mt-2 text-sm text-white/65">Manage workspace identity, seats, and security preferences.</p>
      </div>

      <div className="mt-10 grid gap-8 md:grid-cols-2">
        <article className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-md">
          <p className="text-xs uppercase tracking-[0.14em] text-white/55">Workspace</p>
          <p className="mt-3 text-sm text-white/80">Tenant: demo-brokerage</p>
          <p className="mt-2 text-sm text-white/80">Primary region: US</p>
        </article>
        <article className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-md">
          <p className="text-xs uppercase tracking-[0.14em] text-white/55">Security</p>
          <p className="mt-3 text-sm text-white/80">MFA: Enabled</p>
          <p className="mt-2 text-sm text-white/80">Last access review: February 2026</p>
        </article>
      </div>
    </section>
  );
}

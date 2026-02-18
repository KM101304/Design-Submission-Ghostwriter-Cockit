"use client";

import { useEffect, useMemo, useState } from "react";

type PipelineResponse = {
  profile: {
    submission_id: string;
    insured_name: string | null;
    entity_type: string | null;
    revenue: number | null;
    payroll: number | null;
    locations: Array<{ address: string }>;
    lines_of_business: string[];
    contradictions: string[];
    source_citations?: Record<string, Array<{ source_document: string; page: number | null; snippet: string | null }>>;
  };
  completeness: Array<{
    line_of_business: string;
    completeness_score: number;
    status: string;
    missing_fields: string[];
    blockers: string[];
  }>;
  questions: {
    grouped_questions: Record<string, string[]>;
    email_draft: string;
    bullet_summary: string[];
    plain_english: string;
  };
};

type SubmissionListItem = {
  submission_id: string;
  filename: string;
  content_type: string;
  status: string;
  job_status: string;
  job_id: string | null;
  created_at: string;
};

type AuditLogItem = {
  event_type: string;
  details: string;
  created_at: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const DEMO_EMAIL = process.env.NEXT_PUBLIC_DEMO_EMAIL ?? "admin@ghostwriter.dev";
const DEMO_PASSWORD = process.env.NEXT_PUBLIC_DEMO_PASSWORD ?? "ChangeMe123!";

export default function CockpitPage() {
  const [file, setFile] = useState<File | null>(null);
  const [running, setRunning] = useState(false);
  const [submissions, setSubmissions] = useState<SubmissionListItem[]>([]);
  const [result, setResult] = useState<PipelineResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [tenant, setTenant] = useState<string>("demo-brokerage");
  const [timeline, setTimeline] = useState<string[]>([]);
  const [audits, setAudits] = useState<AuditLogItem[]>([]);

  async function ensureLogin(): Promise<{ token: string; tenantId: string }> {
    if (token) {
      return { token, tenantId: tenant };
    }
    const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: DEMO_EMAIL, password: DEMO_PASSWORD }),
    });
    if (!res.ok) {
      throw new Error("Login failed; check seeded user credentials.");
    }
    const payload = (await res.json()) as { access_token: string; tenant_id: string };
    setToken(payload.access_token);
    setTenant(payload.tenant_id);
    return { token: payload.access_token, tenantId: payload.tenant_id };
  }

  async function authHeaders() {
    const auth = await ensureLogin();
    return {
      Authorization: `Bearer ${auth.token}`,
      "x-tenant-id": auth.tenantId,
    };
  }

  async function loadSubmissions() {
    try {
      const headers = await authHeaders();
      const res = await fetch(`${API_BASE}/api/v1/submissions`, { headers });
      if (!res.ok) {
        return;
      }
      const rows = (await res.json()) as SubmissionListItem[];
      setSubmissions(rows);
    } catch {
      // Keep UI responsive when API is down.
    }
  }

  useEffect(() => {
    void loadSubmissions();
  }, []);

  async function loadAudit(submissionId: string) {
    try {
      const headers = await authHeaders();
      const res = await fetch(`${API_BASE}/api/v1/submissions/${submissionId}/audit`, { headers });
      if (!res.ok) {
        return;
      }
      const rows = (await res.json()) as AuditLogItem[];
      setAudits(rows);
    } catch {
      // noop
    }
  }

  async function runPipeline() {
    if (!file) {
      setError("Select a file first.");
      return;
    }
    setRunning(true);
    setError(null);
    setTimeline(["queued"]);

    const form = new FormData();
    form.append("file", file);

    try {
      const headers = await authHeaders();
      const enqueue = await fetch(`${API_BASE}/api/v1/pipeline/run-async`, {
        method: "POST",
        headers,
        body: form,
      });
      if (!enqueue.ok) {
        const payload = (await enqueue.json()) as { detail?: string };
        throw new Error(payload.detail ?? "Queueing failed");
      }
      const queued = (await enqueue.json()) as { job_id: string; submission_id: string; status: string };
      setTimeline((prev) => [...prev, `job:${queued.job_id}`]);

      const final = await pollJob(queued.job_id);
      setResult(final);
      await loadAudit(final.profile.submission_id);
      await loadSubmissions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setTimeline((prev) => [...prev, "failed"]);
    } finally {
      setRunning(false);
    }
  }

  async function pollJob(jobId: string): Promise<PipelineResponse> {
    for (let attempt = 0; attempt < 80; attempt += 1) {
      const headers = await authHeaders();
      const res = await fetch(`${API_BASE}/api/v1/pipeline/jobs/${jobId}`, { headers });
      if (!res.ok) {
        throw new Error("Job status request failed");
      }
      const payload = (await res.json()) as {
        status: string;
        result?: PipelineResponse;
        error?: string;
      };
      setTimeline((prev) => (prev[prev.length - 1] === payload.status ? prev : [...prev, payload.status]));
      if (payload.status === "succeeded" && payload.result) {
        return payload.result;
      }
      if (payload.status === "failed") {
        throw new Error(payload.error ?? "Pipeline failed");
      }
      await new Promise((resolve) => setTimeout(resolve, 1500));
    }
    throw new Error("Pipeline timed out");
  }

  async function exportArtifact(format: "markdown" | "json" | "pdf") {
    if (!result) return;
    const headers = await authHeaders();
    const res = await fetch(`${API_BASE}/api/v1/submissions/${result.profile.submission_id}/export?format=${format}`, { headers });
    if (!res.ok) {
      setError(`Export ${format} failed`);
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${result.profile.submission_id}.${format === "markdown" ? "md" : format}`;
    link.click();
    URL.revokeObjectURL(url);
  }

  const packetLocked = useMemo(() => {
    if (!result) {
      return false;
    }
    return result.completeness.every((item) => item.status === "Green");
  }, [result]);

  return (
    <main className="min-h-screen p-6">
      <div className="mb-4 rounded-xl border border-white/10 bg-[var(--panel)]/80 px-4 py-3">
        <p className="text-xs uppercase tracking-widest text-[var(--muted)]">Packet State</p>
        <div className="mt-1 flex items-center justify-between gap-4">
          <h1 className="text-xl font-semibold">Submission Ghostwriter Cockpit</h1>
          <span
            className={`rounded-full border px-3 py-1 text-xs ${
              packetLocked
                ? "border-[var(--ok)]/70 bg-[var(--ok)]/10 text-[var(--ok)]"
                : "border-[var(--warn)]/60 bg-[var(--warn)]/10 text-[var(--warn)]"
            }`}
          >
            {packetLocked ? "Packet Locked" : "Packet Unlocked"}
          </span>
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          <input
            type="file"
            accept=".pdf,.txt,.eml"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="max-w-xs rounded border border-white/20 bg-black/20 px-2 py-1 text-xs"
          />
          <button
            onClick={() => void runPipeline()}
            disabled={running}
            className="rounded bg-[var(--accent)] px-3 py-1 text-xs font-medium text-black disabled:opacity-50"
          >
            {running ? "Running..." : "Run Async Pipeline"}
          </button>
          {!running && error && file && (
            <button onClick={() => void runPipeline()} className="rounded border border-[var(--bad)]/50 px-3 py-1 text-xs text-[var(--bad)]">
              Retry
            </button>
          )}
          {result && (
            <>
              <button onClick={() => void exportArtifact("markdown")} className="rounded border border-white/20 px-3 py-1 text-xs">
                Export MD
              </button>
              <button onClick={() => void exportArtifact("json")} className="rounded border border-white/20 px-3 py-1 text-xs">
                Export JSON
              </button>
              <button onClick={() => void exportArtifact("pdf")} className="rounded border border-white/20 px-3 py-1 text-xs">
                Export PDF
              </button>
            </>
          )}
        </div>
        {error && <p className="mt-2 text-xs text-[var(--bad)]">{error}</p>}
      </div>

      <div className="grid gap-4 lg:grid-cols-[280px_1fr_360px]">
        <section className="rounded-xl border border-white/10 bg-[var(--panel)]/80 p-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">Submissions</h2>
          <div className="mt-3 space-y-2">
            {submissions.length === 0 && <p className="text-xs text-[var(--muted)]">No submissions yet.</p>}
            {submissions.map((item) => (
              <article
                key={item.submission_id}
                className="cursor-pointer rounded-lg border border-white/10 bg-black/20 p-3"
                onClick={() => void loadAudit(item.submission_id)}
              >
                <p className="text-xs text-[var(--muted)]">{item.submission_id}</p>
                <p className="text-sm font-medium break-all">{item.filename}</p>
                <p className="mt-1 text-xs text-[var(--muted)]">{item.job_status}</p>
              </article>
            ))}
          </div>

          <div className="mt-4 rounded-lg border border-white/10 bg-black/20 p-3">
            <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Pipeline Timeline</p>
            <ul className="mt-2 space-y-1 text-xs">
              {timeline.map((step, i) => (
                <li key={`${step}-${i}`}>{step}</li>
              ))}
            </ul>
          </div>
        </section>

        <section className="rounded-xl border border-white/10 bg-[var(--panel)]/80 p-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">Risk Profile Summary</h2>
          {result ? (
            <>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <Tile label="Insured" value={result.profile.insured_name ?? "Unknown"} />
                <Tile label="Entity Type" value={result.profile.entity_type ?? "Unknown"} />
                <Tile label="Revenue" value={money(result.profile.revenue)} />
                <Tile label="Payroll" value={money(result.profile.payroll)} />
                <Tile label="Locations" value={String(result.profile.locations.length)} />
                <Tile label="Lines" value={result.profile.lines_of_business.join(", ") || "None"} />
              </div>
              {result.profile.contradictions.length > 0 && (
                <div className="mt-4 rounded-lg border border-[var(--bad)]/40 bg-[var(--bad)]/10 p-3 text-xs">
                  {result.profile.contradictions.join(" ")}
                </div>
              )}

              <div className="mt-4 rounded-lg border border-white/10 bg-black/20 p-3">
                <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Field Citations</p>
                <ul className="mt-2 space-y-1 text-xs">
                  {Object.entries(result.profile.source_citations ?? {}).map(([field, refs]) => (
                    <li key={field}>
                      {field}: {refs[0]?.source_document ?? "unknown"} {refs[0]?.snippet ? `- ${refs[0].snippet}` : ""}
                    </li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <p className="mt-4 text-sm text-[var(--muted)]">Run the pipeline to populate the canonical risk profile.</p>
          )}
        </section>

        <section className="rounded-xl border border-white/10 bg-[var(--panel)]/80 p-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">Completeness + Questions</h2>
          {result ? (
            <>
              {result.completeness.map((item) => (
                <ScoreBar key={item.line_of_business} label={item.line_of_business} value={item.completeness_score} tone={tone(item.status)} />
              ))}

              <div className="mt-4 rounded-lg border border-white/10 bg-black/20 p-3">
                <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Missing Fields</p>
                <ul className="mt-2 space-y-1 text-sm">
                  {result.completeness.flatMap((item) => item.missing_fields).map((field, idx) => (
                    <li key={`${field}-${idx}`}>{field}</li>
                  ))}
                </ul>
              </div>

              <div className="mt-4 rounded-lg border border-white/10 bg-black/20 p-3">
                <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Follow-up Questions</p>
                <ul className="mt-2 space-y-1 text-sm">
                  {result.questions.bullet_summary.map((q, idx) => (
                    <li key={`${q}-${idx}`}>{q}</li>
                  ))}
                </ul>
              </div>

              <div className="mt-4 rounded-lg border border-white/10 bg-black/20 p-3">
                <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Audit Trail</p>
                <ul className="mt-2 space-y-1 text-xs">
                  {audits.map((a, idx) => (
                    <li key={`${a.event_type}-${idx}`}>{new Date(a.created_at).toLocaleTimeString()} {a.event_type}</li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <p className="mt-4 text-sm text-[var(--muted)]">No scoring yet.</p>
          )}
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

function tone(status: string): "ok" | "warn" | "bad" {
  if (status === "Green") return "ok";
  if (status === "Yellow") return "warn";
  return "bad";
}

function money(value: number | null): string {
  if (value == null) return "Unknown";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

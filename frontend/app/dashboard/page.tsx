"use client";

import { AnimatePresence, motion } from "framer-motion";
import { BrainCircuit, FileUp, Lock, Shield, Sparkles } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { AIAlert } from "@/components/cockpit/AIAlert";
import { CompletenessMeter } from "@/components/cockpit/CompletenessMeter";
import { FollowUpPreview } from "@/components/cockpit/FollowUpPreview";
import { PacketLockBanner } from "@/components/cockpit/PacketLockBanner";
import { RiskField } from "@/components/cockpit/RiskField";
import { SubmissionCard } from "@/components/cockpit/SubmissionCard";
import { AuditLogItem, PipelineResponse, SubmissionListItem, UIState } from "@/components/cockpit/types";
import { money, stateLabel } from "@/lib/cockpit";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const DEMO_EMAIL = process.env.NEXT_PUBLIC_DEMO_EMAIL ?? "admin@ghostwriter.dev";
const DEMO_PASSWORD = process.env.NEXT_PUBLIC_DEMO_PASSWORD ?? "ChangeMe123!";

export default function DashboardPage() {
  const [file, setFile] = useState<File | null>(null);
  const [running, setRunning] = useState(false);
  const [submissions, setSubmissions] = useState<SubmissionListItem[]>([]);
  const [selectedSubmissionId, setSelectedSubmissionId] = useState<string | null>(null);
  const [result, setResult] = useState<PipelineResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [tenant, setTenant] = useState<string>("demo-brokerage");
  const [audits, setAudits] = useState<AuditLogItem[]>([]);
  const [copied, setCopied] = useState(false);
  const [uiState, setUiState] = useState<UIState>("Idle");
  const stageTimer = useRef<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  async function ensureLogin(): Promise<{ token: string; tenantId: string }> {
    if (token) return { token, tenantId: tenant };

    const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: DEMO_EMAIL, password: DEMO_PASSWORD }),
    });
    if (!res.ok) throw new Error("Login failed; check seeded user credentials.");

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

  function startStateProgression() {
    if (stageTimer.current) window.clearInterval(stageTimer.current);
    const stages: UIState[] = ["Uploading", "Parsing", "Structuring", "Scoring"];
    let idx = 0;
    setUiState(stages[0]);
    stageTimer.current = window.setInterval(() => {
      idx += 1;
      if (idx < stages.length) setUiState(stages[idx]);
    }, 1100);
  }

  function stopStateProgression() {
    if (stageTimer.current) {
      window.clearInterval(stageTimer.current);
      stageTimer.current = null;
    }
  }

  async function loadSubmissions() {
    try {
      const headers = await authHeaders();
      const res = await fetch(`${API_BASE}/api/v1/submissions`, { headers });
      if (!res.ok) return;
      const rows = (await res.json()) as SubmissionListItem[];
      setSubmissions(rows);
    } catch {
      // noop
    }
  }

  useEffect(() => {
    void loadSubmissions();
    return () => stopStateProgression();
  }, []);

  async function loadAudit(submissionId: string) {
    try {
      const headers = await authHeaders();
      const res = await fetch(`${API_BASE}/api/v1/submissions/${submissionId}/audit`, { headers });
      if (!res.ok) return;
      const rows = (await res.json()) as AuditLogItem[];
      setAudits(rows);
      setSelectedSubmissionId(submissionId);
    } catch {
      // noop
    }
  }

  async function pollJob(jobId: string): Promise<PipelineResponse> {
    for (let attempt = 0; attempt < 80; attempt += 1) {
      const headers = await authHeaders();
      const res = await fetch(`${API_BASE}/api/v1/pipeline/jobs/${jobId}`, { headers });
      if (!res.ok) throw new Error("Job status request failed");

      const payload = (await res.json()) as { status: string; result?: PipelineResponse; error?: string };
      if (payload.status === "succeeded" && payload.result) return payload.result;
      if (payload.status === "failed") throw new Error(payload.error ?? "Pipeline failed");
      await new Promise((resolve) => setTimeout(resolve, 1200));
    }
    throw new Error("Pipeline timed out");
  }

  async function runPipeline() {
    if (!file) {
      setError("Drop a packet before starting AI structuring.");
      return;
    }

    setRunning(true);
    setError(null);
    setAudits([]);
    startStateProgression();

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

      const queued = (await enqueue.json()) as { job_id: string; submission_id: string };
      setSelectedSubmissionId(queued.submission_id);
      const final = await pollJob(queued.job_id);
      setResult(final);
      await loadAudit(final.profile.submission_id);
      await loadSubmissions();

      const locked = final.completeness.every((item) => item.status === "Green");
      setUiState(locked ? "Locked" : "Ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setUiState("Idle");
    } finally {
      stopStateProgression();
      setRunning(false);
    }
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

  async function copyEmailDraft() {
    if (!result?.questions.email_draft) return;
    await navigator.clipboard.writeText(result.questions.email_draft);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  const locked = uiState === "Locked";
  const submissionName = result?.profile.insured_name || file?.name || "New Submission Packet";

  const overallCompleteness = useMemo(() => {
    if (!result || result.completeness.length === 0) return 0;
    return Math.round(result.completeness.reduce((sum, item) => sum + item.completeness_score, 0) / result.completeness.length);
  }, [result]);

  const confidenceScore = useMemo(() => {
    if (!result?.profile.field_confidence) return 0;
    const vals = Object.values(result.profile.field_confidence);
    if (vals.length === 0) return 0;
    return Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 100);
  }, [result]);

  const missingFields = useMemo(() => {
    if (!result) return [];
    const ranked = result.completeness.flatMap((item) =>
      item.missing_fields.map((field) => ({
        field,
        severity: item.blockers.some((blocker) => blocker.toLowerCase().includes(field.toLowerCase())) ? 2 : 1,
      })),
    );
    return ranked.sort((a, b) => b.severity - a.severity).map((item) => item.field);
  }, [result]);

  const renewalDelta = useMemo(() => {
    if (!result) return "Awaiting baseline comparison from current packet.";
    const lines = result.profile.lines_of_business.length;
    if (lines >= 3) return "Coverage scope increased versus typical renewal profile.";
    if ((result.profile.revenue ?? 0) > 3000000) return "Revenue profile indicates likely year-over-year growth.";
    return "No significant change signal detected from renewal assumptions.";
  }, [result]);

  return (
    <section>
      <div className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-md">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-white/60">Submission Cockpit</p>
            <h1 className="mt-2 text-2xl font-semibold text-white">{submissionName}</h1>
            <p className="mt-2 text-sm text-white/65">Upload, structure, resolve blockers, and lock the packet with confidence.</p>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge state={uiState} />
            <motion.div
              animate={locked ? { boxShadow: "0 0 35px rgba(55, 215, 150, 0.35)" } : { boxShadow: "0 0 0 rgba(0, 0, 0, 0)" }}
              className="rounded-xl border border-white/10 bg-black/25 px-4 py-2 text-xs text-white/80"
            >
              {stateLabel(uiState)}
            </motion.div>
          </div>
        </div>

        <div className="mt-8 grid gap-6 sm:grid-cols-3">
          <StatCard label="Confidence" value={`${confidenceScore}%`} />
          <StatCard label="Completeness" value={`${overallCompleteness}%`} />
          <StatCard label="Submission State" value={locked ? "Packet Locked" : "In Progress"} />
        </div>

        <div className="mt-8 grid gap-2 sm:grid-cols-4">
          <StagePill icon={FileUp} active={uiState !== "Idle"} label="Upload" />
          <StagePill icon={BrainCircuit} active={["Parsing", "Structuring", "Scoring", "Ready", "Locked"].includes(uiState)} label="AI Processing" />
          <StagePill icon={Shield} active={uiState === "Ready" || uiState === "Locked"} label="Review" />
          <StagePill icon={Lock} active={uiState === "Locked"} label="Locked" />
        </div>

        <div className="mt-8">
          <PacketLockBanner locked={locked} />
        </div>
      </div>

      <div className="mt-10 grid grid-cols-12 gap-8">
        <aside className="col-span-12 rounded-xl border border-white/10 bg-white/5 p-5 shadow-xl backdrop-blur-md xl:col-span-3">
          <PanelTitle text="Submission Queue" />

          <div className="mt-6 rounded-xl border border-white/10 bg-white/[0.04] p-6">
            <p className="text-sm text-white/70">Drop packet (PDF / EML / TXT)</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.eml"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="mt-4 w-full rounded-lg border border-indigo-300/35 bg-indigo-500/80 px-6 py-3 text-sm font-medium text-white transition hover:bg-indigo-500"
            >
              {file ? `Selected: ${file.name}` : "Select Packet"}
            </button>
            <button
              onClick={() => void runPipeline()}
              disabled={running}
              className="mt-3 w-full rounded-lg bg-emerald-500/90 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:opacity-50"
            >
              {running ? "AI Processing..." : "Upload & Structure"}
            </button>
            {error && <p className="mt-3 text-xs text-rose-300">{error}</p>}
          </div>

          <div className="mt-8 max-h-[460px] space-y-3 overflow-auto pr-1">
            {submissions.map((item) => (
              <SubmissionCard
                key={item.submission_id}
                item={item}
                active={selectedSubmissionId === item.submission_id}
                onClick={() => void loadAudit(item.submission_id)}
              />
            ))}
            {submissions.length === 0 && (
              <p className="rounded-xl border border-white/10 bg-black/20 p-3 text-xs text-white/60">No submissions yet.</p>
            )}
          </div>
        </aside>

        <section className="col-span-12 rounded-xl border border-white/10 bg-white/5 p-5 shadow-xl backdrop-blur-md xl:col-span-6">
          <PanelTitle text="Canonical Risk Profile" />

          <AnimatePresence mode="wait">
            {!result && running && (
              <motion.div
                key="skeleton"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="mt-8 grid gap-6 sm:grid-cols-2"
              >
                {Array.from({ length: 8 }).map((_, idx) => (
                  <div key={idx} className="h-20 animate-pulse rounded-xl border border-white/10 bg-white/[0.03]" />
                ))}
              </motion.div>
            )}

            {!result && !running && (
              <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-8 rounded-xl border border-white/10 bg-black/20 p-6 text-sm text-white/65">
                Begin with packet upload to generate structured risk fields and confidence traces.
              </motion.div>
            )}

            {result && (
              <motion.div key="content" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-8 space-y-6">
                <div className="grid gap-6 sm:grid-cols-2">
                  <RiskField label="Insured Overview" value={result.profile.insured_name ?? "Unknown"} confidence={result.profile.field_confidence?.insured_name} citations={result.profile.source_citations?.insured_name} />
                  <RiskField label="Entity Type" value={result.profile.entity_type ?? "Unknown"} confidence={result.profile.field_confidence?.entity_type} citations={result.profile.source_citations?.entity_type} />
                  <RiskField label="Revenue" value={money(result.profile.revenue)} confidence={result.profile.field_confidence?.revenue} citations={result.profile.source_citations?.revenue} />
                  <RiskField label="Payroll" value={money(result.profile.payroll)} confidence={result.profile.field_confidence?.payroll} citations={result.profile.source_citations?.payroll} />
                  <RiskField label="Locations" value={`${result.profile.locations.length} listed`} confidence={result.profile.field_confidence?.locations} citations={result.profile.source_citations?.locations} />
                  <RiskField label="Prior Losses" value={`${result.profile.prior_losses.length} records`} confidence={result.profile.field_confidence?.prior_losses} citations={result.profile.source_citations?.prior_losses} />
                  <RiskField
                    label="Requested Coverage"
                    value={result.profile.coverage_requested.map((coverage) => coverage.line_of_business).join(", ") || result.profile.lines_of_business.join(", ") || "None listed"}
                    confidence={result.profile.field_confidence?.coverage_requested}
                    citations={result.profile.source_citations?.coverage_requested}
                  />
                </div>

                <AIAlert items={result.profile.contradictions} />

                <div className="rounded-xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-white/60">What Changed Since Renewal</p>
                  <p className="mt-2 text-sm text-white/85">{renewalDelta}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>

        <aside className="col-span-12 space-y-8 xl:col-span-3">
          <article className="rounded-xl border border-white/10 bg-white/5 p-5 shadow-xl backdrop-blur-md">
            <PanelTitle text="AI Intelligence" />
            <div className="mt-6">
              <CompletenessMeter value={overallCompleteness} status={locked ? "Green" : overallCompleteness >= 70 ? "Yellow" : "Red"} />
            </div>

            <details className="mt-6 rounded-xl border border-white/10 bg-black/20 p-4" open>
              <summary className="cursor-pointer text-xs uppercase tracking-[0.16em] text-white/65">Missing Fields</summary>
              <ul className="mt-3 space-y-2 text-sm text-white/90">
                {missingFields.map((field, index) => (
                  <li key={`${field}-${index}`}>{field}</li>
                ))}
                {missingFields.length === 0 && <li className="text-white/60">No missing fields identified.</li>}
              </ul>
            </details>

            {result && (
              <div className="mt-6">
                <FollowUpPreview
                  lines={result.questions.bullet_summary}
                  emailDraft={result.questions.email_draft}
                  onCopy={() => void copyEmailDraft()}
                  copied={copied}
                />
              </div>
            )}
          </article>

          <article className="rounded-xl border border-white/10 bg-white/5 p-5 shadow-xl backdrop-blur-md">
            <PanelTitle text="Export Packet" />
            <div className="mt-6 grid grid-cols-3 gap-3">
              <button onClick={() => void exportArtifact("markdown")} disabled={!result} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-xs disabled:opacity-50">MD</button>
              <button onClick={() => void exportArtifact("json")} disabled={!result} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-xs disabled:opacity-50">JSON</button>
              <button onClick={() => void exportArtifact("pdf")} disabled={!result} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-xs disabled:opacity-50">PDF</button>
            </div>
            <div className="mt-6 flex flex-wrap gap-2">
              {[uiState, ...audits.map((item) => item.event_type)].slice(0, 8).map((step, idx) => (
                <span key={`${step}-${idx}`} className="rounded-full border border-white/20 bg-black/20 px-3 py-1 text-[10px] uppercase tracking-wide text-white/65">
                  {step}
                </span>
              ))}
            </div>
          </article>
        </aside>
      </div>
    </section>
  );
}

function PanelTitle({ text }: { text: string }) {
  return <p className="text-xs uppercase tracking-[0.18em] text-white/60">{text}</p>;
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/25 p-4 shadow-xl">
      <p className="text-xs uppercase tracking-[0.14em] text-white/55">{label}</p>
      <p className="mt-2 text-lg font-semibold text-white">{value}</p>
    </div>
  );
}

function StatusBadge({ state }: { state: UIState }) {
  const tone =
    state === "Locked" || state === "Ready"
      ? "bg-emerald-400/20 text-emerald-200 border-emerald-300/30"
      : state === "Idle"
        ? "bg-white/10 text-white/70 border-white/20"
        : "bg-amber-400/20 text-amber-100 border-amber-300/30";
  return <span className={`rounded-full border px-3 py-1 text-xs font-medium ${tone}`}>{state}</span>;
}

function StagePill({
  icon: Icon,
  active,
  label,
}: {
  icon: typeof FileUp;
  active: boolean;
  label: string;
}) {
  return (
    <div className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-xs ${active ? "border-cyan-300/45 bg-cyan-300/10 text-white" : "border-white/10 bg-black/20 text-white/55"}`}>
      <Icon className="h-3.5 w-3.5" />
      <span>{label}</span>
      {active && <Sparkles className="ml-auto h-3.5 w-3.5 text-cyan-200/80" />}
    </div>
  );
}

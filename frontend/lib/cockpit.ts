import { UIState } from "@/components/cockpit/types";

export function money(value: number | null): string {
  if (value == null) return "Unknown";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

export function toneColor(status: string): string {
  if (status === "Green") return "var(--ok)";
  if (status === "Yellow") return "var(--warn)";
  return "var(--bad)";
}

export function statusTone(status: string): "ok" | "warn" | "bad" | "neutral" {
  const lowered = status.toLowerCase();
  if (lowered.includes("green") || lowered.includes("processed") || lowered.includes("ready") || lowered.includes("locked")) return "ok";
  if (lowered.includes("yellow") || lowered.includes("running") || lowered.includes("queued") || lowered.includes("structuring") || lowered.includes("parsing") || lowered.includes("uploading") || lowered.includes("scoring")) return "warn";
  if (lowered.includes("red") || lowered.includes("failed") || lowered.includes("error")) return "bad";
  return "neutral";
}

export function submissionProgress(jobStatus: string): number {
  const status = jobStatus.toLowerCase();
  if (status.includes("processed")) return 100;
  if (status.includes("running")) return 55;
  if (status.includes("queued")) return 20;
  if (status.includes("failed")) return 12;
  return 0;
}

export function stateLabel(state: UIState): string {
  switch (state) {
    case "Idle":
      return "Waiting for upload";
    case "Uploading":
      return "Uploading packet";
    case "Parsing":
      return "Parsing documents";
    case "Structuring":
      return "Structuring risk profile";
    case "Scoring":
      return "Scoring completeness";
    case "Ready":
      return "Packet structured";
    case "Locked":
      return "Packet locked";
    default:
      return "Processing";
  }
}

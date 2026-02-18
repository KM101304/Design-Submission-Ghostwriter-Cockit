export type UIState = "Idle" | "Uploading" | "Parsing" | "Structuring" | "Scoring" | "Ready" | "Locked";

export type PipelineResponse = {
  profile: {
    submission_id: string;
    insured_name: string | null;
    entity_type: string | null;
    revenue: number | null;
    payroll: number | null;
    locations: Array<{ address: string; city?: string; state?: string }>;
    prior_losses: Array<{ loss_date?: string; amount?: number; description?: string }>;
    coverage_requested: Array<{ line_of_business: string; limit?: string; deductible?: string }>;
    lines_of_business: string[];
    contradictions: string[];
    source_citations?: Record<string, Array<{ source_document: string; page: number | null; snippet: string | null }>>;
    field_confidence?: Record<string, number>;
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

export type SubmissionListItem = {
  submission_id: string;
  filename: string;
  content_type: string;
  status: string;
  job_status: string;
  job_id: string | null;
  created_at: string;
};

export type AuditLogItem = {
  event_type: string;
  details: string;
  created_at: string;
};

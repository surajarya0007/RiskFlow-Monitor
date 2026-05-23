export type WorkflowRecord = {
  id: string;
  name: string;
  status: string;
  type: string;
  latency_ms: number;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type AlertRecord = {
  id: string;
  workflow_id: string;
  severity: string;
  category: string;
  message: string;
  resolved: boolean;
  created_at: string;
};

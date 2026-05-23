const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function fetcher<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-cache" });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchMetrics() {
  return fetcher<{
    workflow_count: number;
    active_alerts: number;
    average_latency_ms: number;
  }>("/api/dashboard/metrics");
}

export async function fetchWorkflows() {
  const data = await fetcher<{ data: unknown[] }>("/api/workflows");
  return data.data as any[];
}

export async function fetchAlerts() {
  const data = await fetcher<{ data: unknown[] }>("/api/alerts");
  return data.data as any[];
}

export async function fetchMarketLatest() {
  const data = await fetcher<{ data: Record<string, { price_usd: number }> }>(
    "/api/market/latest",
  );
  return data.data as Record<string, any>;
}

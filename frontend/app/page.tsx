"use client";

import { useEffect, useMemo } from "react";
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { fetchMetrics, fetchAlerts, fetchWorkflows } from "@/lib/api";
import { fetchMarketLatest } from "@/lib/api";
import StatCard from "@/components/StatCard";
import ActivityFeed from "@/components/ActivityFeed";
import AlertPanel from "@/components/AlertPanel";
import MarketCard from "@/components/MarketCard";

const queryClient = new QueryClient();

function DashboardContent() {
  const queryClient = useQueryClient();

  const metricsQuery = useQuery({
    queryKey: ["metrics"],
    queryFn: fetchMetrics,
    refetchInterval: 10000,
  });
  const marketQuery = useQuery({
    queryKey: ["market"],
    queryFn: fetchMarketLatest,
    refetchInterval: 10000,
  });
  const workflowsQuery = useQuery({
    queryKey: ["workflows"],
    queryFn: fetchWorkflows,
    refetchInterval: 10000,
  });
  const alertsQuery = useQuery({
    queryKey: ["alerts"],
    queryFn: fetchAlerts,
    refetchInterval: 10000,
  });

  useEffect(() => {
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket(
        (process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000") +
          "/ws/stream",
      );
    } catch (e) {
      return;
    }

    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data as string);
        if (msg?.type === "workflow.created") {
          const item = msg.item;
          queryClient.setQueryData(["workflows"], (old: any) => {
            const prior = Array.isArray(old) ? old : (old ?? []);
            const merged = [item, ...prior];
            return merged.slice(0, 10);
          });
        }
      } catch (e) {
        // ignore
      }
    };

    return () => {
      if (ws) ws.close();
    };
  }, [queryClient]);

  const summaryCards = useMemo(
    () => [
      {
        label: "Workflows processed",
        value: metricsQuery.data?.workflow_count ?? 0,
      },
      { label: "Open alerts", value: metricsQuery.data?.active_alerts ?? 0 },
      {
        label: "Avg latency (ms)",
        value: metricsQuery.data?.average_latency_ms ?? 0,
      },
    ],
    [metricsQuery.data],
  );

  return (
    <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <header className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-slate-400">
            GovernanceOps Platform
          </p>
          <h1 className="mt-2 text-4xl font-semibold text-white">
            Operational Monitoring Dashboard
          </h1>
          <p className="mt-2 max-w-2xl text-slate-400">
            Live visibility into workflows, alerts, logs and real-time system
            health.
          </p>
        </div>
      </header>

      <section className="grid gap-4 xl:grid-cols-3">
        {summaryCards.map((card) => (
          <StatCard key={card.label} label={card.label} value={card.value} />
        ))}
      </section>

      <section className="mt-6 grid gap-4 xl:grid-cols-3">
        <MarketCard
          asset="btc"
          price={marketQuery.data?.bitcoin?.price_usd ?? null}
          latency={marketQuery.data?.bitcoin?.latency_ms ?? null}
          status={marketQuery.data?.bitcoin?.request_status ?? null}
        />
        <MarketCard
          asset="eth"
          price={marketQuery.data?.ethereum?.price_usd ?? null}
          latency={marketQuery.data?.ethereum?.latency_ms ?? null}
          status={marketQuery.data?.ethereum?.request_status ?? null}
        />
        <MarketCard
          asset="sol"
          price={marketQuery.data?.solana?.price_usd ?? null}
          latency={marketQuery.data?.solana?.latency_ms ?? null}
          status={marketQuery.data?.solana?.request_status ?? null}
        />
      </section>

      <section className="mt-8 grid gap-6 xl:grid-cols-3">
        <div className="col-span-2 rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-lg shadow-slate-950/20">
          <h2 className="text-xl font-semibold text-white">
            Live workflow activity
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Recent workflow entries across the system.
          </p>
          <ActivityFeed
            workflows={workflowsQuery.data ?? []}
            isLoading={workflowsQuery.isLoading}
          />
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-lg shadow-slate-950/20">
          <h2 className="text-xl font-semibold text-white">Alerts</h2>
          <p className="mt-2 text-sm text-slate-400">
            Active alerts and severity status.
          </p>
          <AlertPanel
            alerts={alertsQuery.data ?? []}
            isLoading={alertsQuery.isLoading}
          />
        </div>
      </section>
    </main>
  );
}

export default function Page() {
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardContent />
    </QueryClientProvider>
  );
}

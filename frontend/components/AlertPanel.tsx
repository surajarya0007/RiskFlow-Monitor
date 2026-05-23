import { AlertRecord } from "@/types";

type AlertPanelProps = {
  alerts: AlertRecord[];
  isLoading: boolean;
};

const severityClasses: Record<string, string> = {
  low: "bg-emerald-500/10 text-emerald-300",
  medium: "bg-amber-500/10 text-amber-300",
  high: "bg-orange-500/10 text-orange-300",
  critical: "bg-rose-500/10 text-rose-300",
};

export default function AlertPanel({ alerts, isLoading }: AlertPanelProps) {
  return (
    <div className="mt-5 space-y-4">
      {isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 text-slate-400">
          Loading alerts…
        </div>
      ) : alerts.length === 0 ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 text-slate-400">
          No alerts currently active.
        </div>
      ) : (
        alerts.slice(0, 6).map((alert) => (
          <div
            key={alert.id}
            className="rounded-3xl border border-slate-800 bg-slate-950/80 p-4"
          >
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-semibold text-white">
                {alert.category}
              </p>
              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${severityClasses[alert.severity] ?? "bg-slate-700 text-slate-200"}`}
              >
                {alert.severity}
              </span>
            </div>
            <p className="mt-3 text-sm text-slate-400">{alert.message}</p>
            <p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate-500">
              {new Date(alert.created_at).toLocaleString()}
            </p>
          </div>
        ))
      )}
    </div>
  );
}

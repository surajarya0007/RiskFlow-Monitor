import { WorkflowRecord } from "@/types";

type ActivityFeedProps = {
  workflows: WorkflowRecord[];
  isLoading: boolean;
};

export default function ActivityFeed({
  workflows,
  isLoading,
}: ActivityFeedProps) {
  return (
    <div className="mt-5 space-y-4">
      {isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 text-slate-400">
          Loading workflow activity…
        </div>
      ) : workflows.length === 0 ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 text-slate-400">
          No workflows found yet.
        </div>
      ) : (
        // show only the latest 10 workflows
        workflows.slice(0, 10).map((workflow) => (
          <div
            key={workflow.id}
            className="rounded-3xl border border-slate-800 bg-slate-950/80 p-5"
          >
            <div className="flex items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-white">
                  {workflow.name}
                </h3>
                <p className="text-sm text-slate-400">Type: {workflow.type}</p>
              </div>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-sm text-slate-300">
                {workflow.status}
              </span>
            </div>
            <div className="mt-4 flex justify-between text-sm text-slate-400">
              <span>Latency {workflow.latency_ms} ms</span>
              <span>{new Date(workflow.created_at).toLocaleString()}</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

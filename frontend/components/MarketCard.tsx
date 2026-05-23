type MarketCardProps = {
  asset: string;
  price?: number | null;
  latency?: number | null;
  status?: string | null;
};

export default function MarketCard({
  asset,
  price,
  latency,
  status,
}: MarketCardProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-lg shadow-slate-950/20">
      <p className="text-sm uppercase tracking-[0.18em] text-slate-500">
        {asset.toUpperCase()}
      </p>
      <p className="mt-4 text-3xl font-semibold text-white">
        {price != null ? `$${price.toLocaleString()}` : "—"}
      </p>
      <div className="mt-3 flex items-center justify-between text-sm text-slate-400">
        <span>Latency: {latency ?? "—"} ms</span>
        <span>Status: {status ?? "—"}</span>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";

export default function StatusPill() {
  const [status, setStatus] = useState<{ ok: boolean; latency?: number } | null>(null);

  async function poll() {
    const start = performance.now();
    try {
      const res = await fetch((process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000") + "/health", { cache: "no-store" });
      const latency = Math.round(performance.now() - start);
      setStatus({ ok: res.ok, latency });
    } catch (e) {
      setStatus({ ok: false });
    }
  }

  useEffect(() => {
    poll();
    const id = setInterval(poll, 30000);
    return () => clearInterval(id);
  }, []);

  if (!status) return <span className="inline-flex items-center px-2 py-1 text-sm rounded-md bg-gray-800 text-gray-200">Checking…</span>;

  const classes = status.ok ? "bg-emerald-600" : "bg-rose-600";
  return (
    <span className={`inline-flex items-center px-2 py-1 text-sm rounded-md ${classes} text-white`}>
      {status.ok ? "API Online" : "API Offline"}
      {status.latency ? <span className="ml-2 text-xs opacity-80">{status.latency}ms</span> : null}
    </span>
  );
}

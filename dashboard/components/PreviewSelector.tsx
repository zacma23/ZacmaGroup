"use client";

import { useEffect, useState } from "react";
import { usePreview } from "./PreviewProvider";

export default function PreviewSelector({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { enterPreview } = usePreview();
  const [name, setName] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
    fetch(`${apiBase}/api/v1/crm/leads`).then((r) => r.json()).then((data) => {
      if (Array.isArray(data)) {
        const names = data.slice(0, 8).map((d: any) => (d.name ?? d.full_name ?? d.email ?? "Sample Customer"));
        setSuggestions(names);
      }
    }).catch(() => {
      setSuggestions(["Sample Customer", "Test User", "Jane Doe"]);
    }).finally(() => setLoading(false));
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-slate-800 p-4 rounded w-full max-w-md">
        <h3 className="text-lg font-semibold">Preview as Customer</h3>
        <p className="text-sm text-gray-300 mt-2">Select a customer or enter a name/email to preview.</p>
        <input
          className="mt-3 w-full px-3 py-2 bg-slate-900 border border-gray-700 rounded text-white"
          placeholder="Customer name or email"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoFocus
        />

        <div className="mt-3 text-sm text-gray-300">
          {loading ? "Loading suggestions…" : (
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s) => (
                <button key={s} className="px-2 py-1 bg-gray-800 rounded text-sm" onClick={() => setName(s)}>
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="mt-4 flex justify-end gap-2">
          <button className="px-3 py-1 text-sm rounded bg-gray-700" onClick={onClose}>
            Cancel
          </button>
          <button
            className="px-3 py-1 text-sm rounded bg-indigo-600"
            onClick={() => {
              enterPreview(name || "Sample Customer");
              onClose();
            }}
          >
            Enter Preview
          </button>
        </div>
      </div>
    </div>
  );
}

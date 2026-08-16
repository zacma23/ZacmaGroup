"use client";

import React, { useState, useEffect } from "react";

type Field = {
  name: string;
  label: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
};

export default function ProfessionalForm({
  endpoint,
  fields,
  sample,
  submitLabel = "Create",
}: {
  endpoint: string;
  fields: Field[];
  sample?: Record<string, any> | null;
  submitLabel?: string;
}) {
  const [values, setValues] = useState<Record<string, any>>(() => {
    const init: Record<string, any> = {};
    fields.forEach((f) => (init[f.name] = sample?.[f.name] ?? ""));
    return init;
  });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState<string | null>(null);

  useEffect(() => {
    const c = typeof document !== "undefined" ? document.cookie : "";
    const m = c.split(";").map((s) => s.trim()).find((p) => p.startsWith("zacma_preview_customer="));
    setPreviewMode(m ? m.split("=")[1] : null);
  }, []);

  function setField(name: string, v: any) {
    setValues((prev) => ({ ...prev, [name]: v }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMessage(null);
    if (previewMode) {
      setMessage("Preview mode active — write actions are disabled.");
      return;
    }

    // basic validation
    for (const f of fields) {
      if (f.required && !values[f.name]) {
        setMessage(`${f.label} is required`);
        return;
      }
    }

    setSubmitting(true);
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
      const res = await fetch(apiBase + endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      if (res.ok) {
        setMessage("Saved successfully.");
      } else {
        const text = await res.text();
        setMessage("Error: " + (text || res.statusText));
      }
    } catch (err: any) {
      setMessage("Network error: " + String(err?.message ?? err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl">
      <div className="bg-slate-800 border border-gray-700 rounded p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {fields.map((f) => (
            <div key={f.name}>
              <label className="block text-sm text-gray-300 mb-1">{f.label}{f.required ? " *" : ""}</label>
              {f.type === "textarea" ? (
                <textarea
                  value={values[f.name]}
                  onChange={(e) => setField(f.name, e.target.value)}
                  placeholder={f.placeholder}
                  className="w-full bg-slate-900 border border-gray-700 rounded px-3 py-2 text-sm text-gray-100"
                />
              ) : (
                <input
                  type={f.type ?? "text"}
                  value={values[f.name]}
                  onChange={(e) => setField(f.name, e.target.value)}
                  placeholder={f.placeholder}
                  className="w-full bg-slate-900 border border-gray-700 rounded px-3 py-2 text-sm text-gray-100"
                />
              )}
            </div>
          ))}
        </div>

        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-gray-300">{message}</div>
          <div className="flex items-center gap-2">
            <button
              type="submit"
              disabled={submitting || !!previewMode}
              className={`px-3 py-1 text-sm rounded ${submitting || previewMode ? "bg-gray-700 text-gray-400" : "bg-emerald-600 text-white"}`}>
              {submitting ? "Saving…" : submitLabel}
            </button>
          </div>
        </div>
      </div>
    </form>
  );
}

"use client";

import React, { useState } from "react";
import { useAuth } from "./AuthProvider";

export default function LoginModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email.trim(),
          password: password,
          remember_me: true,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Authentication failed. Please check your credentials.");
      }

      login(data.role, data.email, data.access_token, data.full_name);
      onClose();
    } catch (err: any) {
      setError(err.message || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="bg-slate-800 p-5 rounded-lg w-full max-w-sm border border-gray-700 text-white shadow-xl">
        <h3 className="text-lg font-semibold">Sign in</h3>
        <p className="text-xs text-gray-300 mt-1">Sign in with your registered account or administrator credentials.</p>

        {error && (
          <div className="mt-3 p-2 bg-red-950 border border-red-800 text-red-300 text-xs rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleAuth} className="mt-3 space-y-3">
          <div>
            <label className="text-xs text-gray-300">Email</label>
            <input
              type="email"
              required
              className="mt-1 w-full px-3 py-2 bg-slate-900 border border-gray-700 rounded text-sm text-white focus:outline-none focus:border-emerald-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="zacma@admin or you@example.com"
            />
          </div>

          <div>
            <label className="text-xs text-gray-300">Password</label>
            <input
              type="password"
              required
              className="mt-1 w-full px-3 py-2 bg-slate-900 border border-gray-700 rounded text-sm text-white focus:outline-none focus:border-emerald-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          <div className="mt-4 flex justify-end gap-2 pt-2 border-t border-gray-700">
            <button
              type="button"
              className="px-3 py-1.5 text-xs rounded bg-gray-700 hover:bg-gray-600 text-gray-200"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-1.5 text-xs rounded bg-emerald-600 hover:bg-emerald-500 text-white font-medium disabled:opacity-50"
            >
              {loading ? "Authenticating..." : "Sign in"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

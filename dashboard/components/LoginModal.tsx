"use client";

import { useState } from "react";
import { useAuth } from "./AuthProvider";

export default function LoginModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { login } = useAuth();
  const [role, setRole] = useState("admin");
  const [email, setEmail] = useState("");

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-slate-800 p-4 rounded w-full max-w-sm">
        <h3 className="text-lg font-semibold">Sign in (local)</h3>
        <p className="text-sm text-gray-300 mt-2">Choose a role to simulate: admin, staff, or customer.</p>
        <div className="mt-3">
          <label className="text-sm text-gray-300">Email</label>
          <input className="mt-1 w-full px-3 py-2 bg-slate-900 border border-gray-700 rounded text-white" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
        </div>
        <div className="mt-3">
          <label className="text-sm text-gray-300">Role</label>
          <select className="mt-1 w-full px-3 py-2 bg-slate-900 border border-gray-700 rounded text-white" value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="admin">Admin</option>
            <option value="staff">Staff</option>
            <option value="customer">Customer</option>
          </select>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <button className="px-3 py-1 text-sm rounded bg-gray-700" onClick={onClose}>Cancel</button>
          <button className="px-3 py-1 text-sm rounded bg-emerald-600" onClick={() => { login(role, email || undefined); onClose(); }}>Sign in</button>
        </div>
      </div>
    </div>
  );
}

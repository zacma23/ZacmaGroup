"use client";

import Link from "next/link";
import { useState } from "react";
import StatusPill from "./StatusPill";
import { usePreview } from "./PreviewProvider";
import PreviewSelector from "./PreviewSelector";
import LoginModal from "./LoginModal";
import { useSidebar } from "./SidebarProvider";
import { useAuth } from "./AuthProvider";

export default function TopBar() {
  const { previewMode, enterPreview, exitPreview, customerName } = usePreview();
  const [open, setOpen] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const { toggle } = useSidebar();
  const { role, email, login, logout } = useAuth();

  return (
    <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-slate-900">
      <div className="flex items-center gap-4">
        <button className="md:hidden p-2 mr-1 rounded hover:bg-slate-800" onClick={() => toggle()} aria-label="Open sidebar">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12h18M3 6h18M3 18h18"></path></svg>
        </button>
        <div className="text-sm font-semibold">ZACMA Ops</div>
        <div className="text-xs text-gray-300 hidden sm:block">Acme Tenant</div>
      </div>

      <div className="flex items-center gap-3">
        <StatusPill />
        <button className="px-2 py-1 text-sm rounded bg-gray-800 text-gray-200" onClick={() => setOpen(true)}>
          {previewMode ? `Previewing as ${customerName}` : "Preview as Customer"}
        </button>
        {previewMode ? (
          <button className="px-2 py-1 text-sm rounded bg-rose-600 text-white" onClick={() => exitPreview()}>
            Exit Preview
          </button>
        ) : null}

        {role ? (
          <div className="flex items-center gap-3">
            <div className="text-sm text-gray-200">{role}{email ? ` • ${email}` : ''}</div>
            <button className="px-2 py-1 text-sm rounded bg-gray-700" onClick={() => logout()}>Sign out</button>
          </div>
        ) : (
          <button className="px-2 py-1 text-sm rounded bg-emerald-600" onClick={() => {
            // open login modal
            setLoginOpen(true);
          }}>
            Sign in
          </button>
        )}
      </div>

      <PreviewSelector open={open} onClose={() => setOpen(false)} />
      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    </div>
  );
}

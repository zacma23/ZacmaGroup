"use client";

import Link from "next/link";
import ModuleIconMap from "./icons";
import { useSidebar } from "./SidebarProvider";
import AuthAdminLinks from "./AuthAdminLinks";

const modules = [
  { key: "crm", label: "CRM", href: "/dashboard/crm" },
  { key: "people", label: "People", href: "/dashboard/people" },
  { key: "payments", label: "Payments", href: "/dashboard/payments" },
  { key: "training", label: "Training", href: "/dashboard/training" },
  { key: "travel", label: "Travel", href: "/dashboard/travel" },
  { key: "visa", label: "Visa", href: "/dashboard/visa" },
  { key: "marketing", label: "Marketing", href: "/dashboard/marketing" },
];

export default function Sidebar() {
  const { open, setOpen } = useSidebar();

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="w-64 min-h-screen bg-slate-950 border-r border-gray-800 p-3 hidden md:block">
        <div className="mb-6 px-2 text-lg font-bold">Dashboard</div>
        <nav className="flex flex-col gap-1">
          {modules.map((m) => {
            const Icon = ModuleIconMap[m.key] ?? ModuleIconMap["crm"];
            return (
              <Link key={m.key} href={m.href} className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-gray-200">
                <Icon size={16} />
                <span>{m.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-6 px-2 text-xs text-gray-400">Administration</div>
        <nav className="flex flex-col gap-1 mt-2">
          <AuthAdminLinks />
        </nav>
      </aside>

      {/* Mobile drawer */}
      {open ? (
        <div className="md:hidden fixed inset-0 z-40">
          <div className="absolute inset-0 bg-black opacity-50" onClick={() => setOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-72 bg-slate-950 border-r border-gray-800 p-4 overflow-auto">
            <div className="mb-6 px-2 flex items-center justify-between">
              <div className="text-lg font-bold">Dashboard</div>
              <button className="p-2 rounded hover:bg-slate-900" onClick={() => setOpen(false)} aria-label="Close sidebar">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>
            <nav className="flex flex-col gap-1">
              {modules.map((m) => {
                const Icon = ModuleIconMap[m.key] ?? ModuleIconMap["crm"];
                return (
                  <Link key={m.key} href={m.href} className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-gray-200" onClick={() => setOpen(false)}>
                    <Icon size={16} />
                    <span>{m.label}</span>
                  </Link>
                );
              })}
            </nav>

            <div className="mt-6 px-2 text-xs text-gray-400">Administration</div>
            <nav className="flex flex-col gap-1 mt-2">
              <AuthAdminLinks onClick={() => setOpen(false)} />
            </nav>
          </div>
        </div>
      ) : null}
    </>
  );
}

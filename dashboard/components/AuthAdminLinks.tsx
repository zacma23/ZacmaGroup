"use client";

import Link from "next/link";
import { useAuth } from "./AuthProvider";

export default function AuthAdminLinks({ onClick }: { onClick?: () => void }) {
  const { role } = useAuth();
  if (role !== "admin" && role !== "staff") {
    return (
      <div className="px-3 py-2 text-xs text-gray-500">
        Admin & staff links restricted.
      </div>
    );
  }

  return (
    <>
      <Link
        href="/dashboard/admin/search"
        className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-cyan-300 font-medium"
        onClick={onClick}
      >
        <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
        <span>Global Search & AI</span>
      </Link>
      <Link
        href="/dashboard/admin/reviews"
        className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-amber-300 font-medium"
        onClick={onClick}
      >
        <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
        <span>Client Case Reviews</span>
      </Link>
      <Link
        href="/dashboard/admin/inbox"
        className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-gray-200"
        onClick={onClick}
      >
        <span>Support Inbox</span>
      </Link>
      <Link
        href="/dashboard/admin/packages"
        className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-gray-200"
        onClick={onClick}
      >
        <span>Package Catalog</span>
      </Link>
      <Link
        href="/dashboard/admin/users"
        className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-gray-200"
        onClick={onClick}
      >
        <span>Users</span>
      </Link>
      <Link
        href="/dashboard/admin/tenants"
        className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-gray-200"
        onClick={onClick}
      >
        <span>Tenants</span>
      </Link>
      <Link
        href="/dashboard/admin/audit"
        className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-gray-200"
        onClick={onClick}
      >
        <span>Audit Logs</span>
      </Link>
    </>
  );
}

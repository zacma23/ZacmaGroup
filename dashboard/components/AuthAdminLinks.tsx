"use client";

import Link from "next/link";
import { useAuth } from "./AuthProvider";

export default function AuthAdminLinks({ onClick }: { onClick?: () => void }){
  const { role } = useAuth();
  if(role !== "admin"){
    return (
      <>
        <div className="px-3 py-2 text-sm text-gray-400">Admin links hidden (admin role required)</div>
      </>
    );
  }

  return (
    <>
      <Link href="/dashboard/admin/users" className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-gray-200" onClick={onClick}>Users</Link>
      <Link href="/dashboard/admin/tenants" className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-gray-200" onClick={onClick}>Tenants</Link>
      <Link href="/dashboard/admin/audit" className="flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-900 text-sm text-gray-200" onClick={onClick}>Audit</Link>
    </>
  );
}

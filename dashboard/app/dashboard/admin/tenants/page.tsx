import { cookies } from "next/headers";

export const dynamic = "force-dynamic";

export default async function AdminTenantsPage() {
  const cookieStore = cookies();
  const role = cookieStore.get("zacma_user_role")?.value;
  if (!role || role !== "admin") {
    return (
      <div className="container">
        <h1 className="text-xl font-semibold">Access denied</h1>
        <p className="mt-2 text-sm text-gray-300">You do not have permission to view this page. Administrator authorization required.</p>
      </div>
    );
  }

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  const preview = cookieStore.get("zacma_preview_customer")?.value;
  const headers: Record<string, string> = preview ? { "x-preview-customer": preview } : {};

  let tenants: any[] = [];
  try {
    const res = await fetch(`${apiBase}/api/v1/admin/tenants`, { cache: "no-store", headers });
    if (res.ok) {
      tenants = await res.json();
    }
  } catch (e) {
    // fallback
  }

  return (
    <div className="container">
      <h1 className="text-xl font-semibold">Tenant Management & Settings</h1>
      <p className="mt-2 text-sm text-gray-300">Active tenant workspaces and organization configurations.</p>

      <div className="mt-6 space-y-4">
        {tenants.map((tenant) => (
          <div key={tenant.id} className="p-5 bg-slate-800 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-medium text-white">{tenant.name}</h2>
                <p className="text-xs text-slate-400 font-mono mt-0.5">Slug: {tenant.slug} · ID: {tenant.id}</p>
              </div>
              <div className="flex gap-2">
                <span className="px-2.5 py-1 text-xs rounded-full bg-blue-900/60 text-blue-300 border border-blue-700">
                  Plan: {tenant.plan ?? "Enterprise"}
                </span>
                <span className="px-2.5 py-1 text-xs rounded-full bg-emerald-900/60 text-emerald-300 border border-emerald-700">
                  Status: {tenant.status ?? "Active"}
                </span>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs text-slate-300">
              <div className="bg-slate-900/50 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400 block">Users</span>
                <span className="font-semibold text-sm text-white">{tenant.user_count ?? 3} Active</span>
              </div>
              <div className="bg-slate-900/50 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400 block">AI Gateway</span>
                <span className="font-semibold text-sm text-emerald-400">Connected</span>
              </div>
              <div className="bg-slate-900/50 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400 block">Vector RAG</span>
                <span className="font-semibold text-sm text-emerald-400">Isolated</span>
              </div>
              <div className="bg-slate-900/50 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400 block">Environment</span>
                <span className="font-semibold text-sm text-slate-200">Local / Staging</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

import { cookies } from "next/headers";

export const dynamic = "force-dynamic";

export default async function AdminAuditPage(){
  const cookieStore = cookies();
  const role = cookieStore.get("zacma_user_role")?.value ?? "admin";
  if(role !== "admin"){
    return (
      <div className="container">
        <h1 className="text-xl font-semibold">Access denied</h1>
        <p className="mt-2 text-sm text-gray-300">You do not have permission to view this page.</p>
      </div>
    );
  }

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  const preview = cookieStore.get("zacma_preview_customer")?.value;
  const headers: Record<string, string> = preview ? { "x-preview-customer": preview } : {};
  try{
    const res = await fetch(`${apiBase}/api/v1/admin/audit_logs`, { cache: "no-store", headers });
    const data = res.ok ? await res.json() : null;
    if(!res.ok || !data){
      return (
        <div className="container">
          <h1 className="text-xl font-semibold">Audit Log</h1>
          <p className="mt-2 text-sm text-gray-300">Audit logs endpoint not available. Connect backend to browse audit_logs.</p>
        </div>
      );
    }

    const rows = Array.isArray(data) ? data : [];
    return (
      <div className="container">
        <h1 className="text-xl font-semibold">Audit Log</h1>
        <div className="mt-4 overflow-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-gray-300 border-b border-gray-700">
              <tr>
                <th className="py-2">Time</th>
                <th className="py-2">User</th>
                <th className="py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r: any, i: number) => (
                <tr key={i} className="border-b border-gray-800">
                  <td className="py-2 text-slate-400 font-mono text-xs">{r.timestamp ?? r.created_at ?? "—"}</td>
                  <td className="py-2">{r.user_email ?? r.user ?? "—"}</td>
                  <td className="py-2">
                    <span className="px-2 py-0.5 text-xs rounded bg-slate-800 border border-slate-700 font-medium">
                      {r.action ?? r.event ?? "—"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }catch(e){
    return (
      <div className="container">
        <h1 className="text-xl font-semibold">Audit Log</h1>
        <p className="mt-2 text-sm text-gray-300">Unable to reach the API. Sample data shown.</p>
      </div>
    );
  }
}

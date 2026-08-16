export default async function AdminUsersPage(){
  // Role guard reading role from request cookies
  const { cookies } = await import('next/headers');
  const cookieStore = cookies();
  const role = cookieStore.get('zacma_user_role')?.value ?? "admin";
  if (role !== "admin") {
    return (
      <div className="container">
        <h1 className="text-xl font-semibold">Access denied</h1>
        <p className="mt-2 text-sm text-gray-300">You do not have permission to view this page.</p>
      </div>
    );
  }

  // Attempt to fetch user profiles from backend; if missing, show sample message
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  const preview = cookieStore.get('zacma_preview_customer')?.value;
  const headers: Record<string, string> = preview ? { 'x-preview-customer': preview } : {};

  try {
    const res = await fetch(`${apiBase}/api/v1/admin/users`, { cache: "no-store", headers });
    const data = res.ok ? await res.json() : null;

    if(!res.ok || !data){
      return (
        <div className="container">
          <h1 className="text-xl font-semibold">User & Role Management</h1>
          <p className="mt-2 text-sm text-gray-300">No live user list available — the backend endpoint /api/v1/admin/users is not present. Show sample data or connect backend.</p>
        </div>
      );
    }

    const rows = Array.isArray(data) ? data : [];

    return (
      <div className="container">
        <h1 className="text-xl font-semibold">User & Role Management</h1>
        <div className="mt-4 overflow-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-gray-300 border-b border-gray-700">
              <tr>
                <th className="py-2">ID</th>
                <th className="py-2">Email</th>
                <th className="py-2">Role</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r: any) => (
                <tr key={r.id} className="border-b border-gray-800">
                  <td className="py-2">{r.id}</td>
                  <td className="py-2">{r.email ?? r.user_email ?? "—"}</td>
                  <td className="py-2">{r.role ?? r.user_role ?? "—"}</td>
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
        <h1 className="text-xl font-semibold">User & Role Management</h1>
        <p className="mt-2 text-sm text-gray-300">Unable to reach the API. Sample data shown.</p>
      </div>
    );
  }
}

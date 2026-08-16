import ProfessionalForm from "../../../components/ProfessionalForm";

export default async function CRMPage(){
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  try{
    const { cookies } = await import('next/headers');
    const cookieStore = cookies();
    const preview = cookieStore.get('zacma_preview_customer')?.value;
    const headers: Record<string, string> = preview ? { 'x-preview-customer': preview } : {};

    const res = await fetch(`${apiBase}/api/v1/crm/leads`, { cache: "no-store", headers });
    const data = res.ok ? await res.json() : null;

    const rows = Array.isArray(data) ? data : [];

    return (
      <div className="container">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold">CRM — Leads</h1>
          <div className="text-sm text-gray-300">{preview ? `Previewing as ${preview}` : "Live data"}</div>
        </div>

        <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 bg-slate-800 border border-gray-700 rounded p-4">
            <h2 className="text-sm font-medium text-gray-200">Recent leads</h2>
            {rows.length === 0 ? (
              <p className="mt-2 text-xs text-gray-400">No live leads found. Sample data will appear here when a tenant is connected.</p>
            ) : (
              <ul className="mt-3 space-y-2 max-h-72 overflow-auto">
                {rows.slice(0, 20).map((r: any) => (
                  <li key={r.id} className="text-sm text-gray-100 border-b border-gray-700 py-2">
                    <div className="font-medium">{r.name ?? r.full_name ?? "—"}</div>
                    <div className="text-xs text-gray-400">{r.email ?? "—"}</div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="lg:col-span-2">
            <h3 className="text-sm text-gray-300 mb-2">Create new lead</h3>
            {/* @ts-ignore Server component rendering a client component */}
            <ProfessionalForm
              endpoint="/api/v1/crm/leads"
              fields={[
                { name: "name", label: "Full name", required: true, placeholder: "Jane Doe" },
                { name: "email", label: "Email", type: "email", required: true, placeholder: "jane@example.com" },
                { name: "company", label: "Company", placeholder: "Acme Ltd" },
                { name: "phone", label: "Phone", placeholder: "+44 7123 456789" },
                { name: "notes", label: "Notes", type: "textarea", placeholder: "Context or notes" },
              ]}
              submitLabel="Add lead"
            />
          </div>
        </div>
      </div>
    );
  }catch(e){
    return (
      <div className="container">
        <h1 className="text-xl font-semibold">CRM</h1>
        <p className="mt-2 text-sm text-gray-300">Unable to reach the API. Sample data shown.</p>
      </div>
    );
  }
}

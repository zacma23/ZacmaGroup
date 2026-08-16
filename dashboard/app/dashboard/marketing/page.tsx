import ProfessionalForm from "../../../components/ProfessionalForm";

export default async function MarketingPage(){
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  try{
    const { cookies } = await import('next/headers');
    const cookieStore = cookies();
    const preview = cookieStore.get('zacma_preview_customer')?.value;
    const headers: Record<string, string> = preview ? { 'x-preview-customer': preview } : {};

    const res = await fetch(`${apiBase}/api/v1/marketing/campaigns`, { cache: "no-store", headers });
    const data = res.ok ? await res.json() : null;

    const rows = Array.isArray(data) ? data : [];

    return (
      <div className="container">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold">Marketing — Campaigns</h1>
          <div className="text-sm text-gray-300">{preview ? `Previewing as ${preview}` : "Live data"}</div>
        </div>

        <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 bg-slate-800 border border-gray-700 rounded p-4">
            <h2 className="text-sm font-medium text-gray-200">Active campaigns</h2>
            {rows.length === 0 ? (
              <p className="mt-2 text-xs text-gray-400">No campaigns found. Sample campaigns will appear when connected.</p>
            ) : (
              <ul className="mt-3 space-y-2 max-h-72 overflow-auto">
                {rows.slice(0, 20).map((r: any) => (
                  <li key={r.id} className="text-sm text-gray-100 border-b border-gray-700 py-2">
                    <div className="font-medium">{r.name ?? r.title ?? "—"}</div>
                    <div className="text-xs text-gray-400">Status: {r.status ?? "—"}</div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="lg:col-span-2">
            <h3 className="text-sm text-gray-300 mb-2">Create campaign</h3>
            {/* @ts-ignore */}
            <ProfessionalForm
              endpoint="/api/v1/marketing/campaigns"
              fields={[
                { name: "name", label: "Campaign name", required: true, placeholder: "Acquisition Q3" },
                { name: "channel", label: "Channel", placeholder: "email, social, ads" },
                { name: "start_date", label: "Start date", type: "date" },
                { name: "budget", label: "Budget (USD)", type: "number", placeholder: "5000" },
                { name: "description", label: "Description", type: "textarea", placeholder: "Campaign brief" },
              ]}
              submitLabel="Create campaign"
            />
          </div>
        </div>
      </div>
    );
  }catch(e){
    return (
      <div className="container">
        <h1 className="text-xl font-semibold">Marketing</h1>
        <p className="mt-2 text-sm text-gray-300">Unable to reach the API. Sample data shown.</p>
      </div>
    );
  }
}

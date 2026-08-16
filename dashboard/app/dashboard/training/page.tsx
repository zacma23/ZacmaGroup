import ProfessionalForm from "../../../components/ProfessionalForm";

export default async function TrainingPage(){
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  try{
    const { cookies } = await import('next/headers');
    const cookieStore = cookies();
    const preview = cookieStore.get('zacma_preview_customer')?.value;
    const headers: Record<string, string> = preview ? { 'x-preview-customer': preview } : {};

    const res = await fetch(`${apiBase}/api/v1/training/courses`, { cache: "no-store", headers });
    const data = res.ok ? await res.json() : null;

    const rows = Array.isArray(data) ? data : [];

    return (
      <div className="container">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold">Training — Courses</h1>
          <div className="text-sm text-gray-300">{preview ? `Previewing as ${preview}` : "Live data"}</div>
        </div>

        <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 bg-slate-800 border border-gray-700 rounded p-4">
            <h2 className="text-sm font-medium text-gray-200">Available courses</h2>
            {rows.length === 0 ? (
              <p className="mt-2 text-xs text-gray-400">No courses found. Sample courses will appear when connected.</p>
            ) : (
              <ul className="mt-3 space-y-2 max-h-72 overflow-auto">
                {rows.slice(0, 20).map((r: any) => (
                  <li key={r.id} className="text-sm text-gray-100 border-b border-gray-700 py-2">
                    <div className="font-medium">{r.title ?? r.name ?? "—"}</div>
                    <div className="text-xs text-gray-400">Enrolled: {r.enrolled_count ?? r.participants ?? 0}</div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="lg:col-span-2">
            <h3 className="text-sm text-gray-300 mb-2">Create course</h3>
            {/* @ts-ignore */}
            <ProfessionalForm
              endpoint="/api/v1/training/courses"
              fields={[
                { name: "title", label: "Course title", required: true, placeholder: "Intro to ZACMA" },
                { name: "description", label: "Description", type: "textarea", placeholder: "Course summary" },
                { name: "capacity", label: "Capacity", type: "number", placeholder: "20" },
                { name: "start_date", label: "Start date", type: "date" },
              ]}
              submitLabel="Create course"
            />
          </div>
        </div>
      </div>
    );
  }catch(e){
    return (
      <div className="container">
        <h1 className="text-xl font-semibold">Training</h1>
        <p className="mt-2 text-sm text-gray-300">Unable to reach the API. Sample data shown.</p>
      </div>
    );
  }
}

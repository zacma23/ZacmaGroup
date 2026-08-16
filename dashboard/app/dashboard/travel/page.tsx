export default async function TravelPage(){
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  try{
    const { cookies } = await import('next/headers');
    const cookieStore = cookies();
    const preview = cookieStore.get('zacma_preview_customer')?.value;
    const headers: Record<string, string> = preview ? { 'x-preview-customer': preview } : {};

    const res = await fetch(`${apiBase}/api/v1/travel/bookings`, { cache: "no-store", headers });
    const data = res.ok ? await res.json() : null;

    if(!res.ok || !data) {
      return (
        <div className="container">
          <h1 className="text-xl font-semibold">Travel</h1>
          <p className="mt-2 text-sm text-gray-300">Sample data — connect a tenant session to see live records.</p>
        </div>
      );
    }

    const rows = Array.isArray(data) ? data : [];

    return (
      <div className="container">
        <h1 className="text-xl font-semibold">Bookings</h1>
        <div className="mt-4 overflow-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-gray-300 border-b border-gray-700">
              <tr>
                <th className="py-2">ID</th>
                <th className="py-2">Traveler</th>
                <th className="py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r: any) => (
                <tr key={r.id} className="border-b border-gray-800">
                  <td className="py-2">{r.id}</td>
                  <td className="py-2">{r.traveler_name ?? r.passenger ?? "—"}</td>
                  <td className="py-2">{r.status ?? "—"}</td>
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
        <h1 className="text-xl font-semibold">Travel</h1>
        <p className="mt-2 text-sm text-gray-300">Unable to reach the API. Sample data shown.</p>
      </div>
    );
  }
}

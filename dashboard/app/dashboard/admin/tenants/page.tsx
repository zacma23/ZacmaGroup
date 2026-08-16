export default async function AdminTenantsPage(){
  const { cookies } = await import('next/headers');
  const cookieStore = cookies();
  const role = cookieStore.get('zacma_user_role')?.value ?? "admin";
  if(role !== "admin"){
    return (
      <div className="container">
        <h1 className="text-xl font-semibold">Access denied</h1>
        <p className="mt-2 text-sm text-gray-300">You do not have permission to view this page.</p>
      </div>
    );
  }

  return (
    <div className="container">
      <h1 className="text-xl font-semibold">Tenant Settings</h1>
      <p className="mt-2 text-sm text-gray-300">Tenant settings and branding controls will appear here (logo_url, primary_color, etc.).</p>
    </div>
  );
}

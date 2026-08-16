import Dashboard from "../components/dashboard";
import { getDashboardData } from "../lib/dashboard-data";

export const dynamic = "force-dynamic";

export default async function Home() {
  const initialData = await getDashboardData();

  return <Dashboard initialData={initialData} />;
}

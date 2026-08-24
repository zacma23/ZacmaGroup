"use client";

import { useEffect, useState } from "react";
import {
  TrendingUp,
  DollarSign,
  Briefcase,
  CheckCircle2,
  Clock,
  Plus,
  Search,
  Filter,
  Users,
  PhoneCall,
  Mail,
  Calendar,
  MessageSquare,
  Building2,
  X,
  ArrowRight,
  ChevronRight,
} from "lucide-react";

export default function CRMPage() {
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

  const [activeTab, setActiveTab] = useState<"pipeline" | "opportunities" | "activities" | "contacts">("pipeline");
  const [pipelineData, setPipelineData] = useState<any | null>(null);
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [activities, setActivities] = useState<any[]>([]);
  const [contacts, setContacts] = useState<any[]>([]);
  const [people, setPeople] = useState<any[]>([]);
  const [organizations, setOrganizations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  // New Deal Modal
  const [showNewDealModal, setShowNewDealModal] = useState(false);
  const [newDealForm, setNewDealForm] = useState({
    title: "",
    person_id: "",
    organization_id: "",
    value: 50000,
    currency: "ETB",
    pipeline_stage: "New Lead",
    probability: 20,
    expected_close_date: "",
    notes: "",
  });

  // New Activity Modal
  const [showNewActModal, setShowNewActModal] = useState(false);
  const [newActForm, setNewActForm] = useState({
    activity_type: "Call",
    subject: "",
    description: "",
    person_id: "",
    opportunity_id: "",
    due_date: "",
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [pipeRes, oppsRes, actsRes, contactsRes, peopleRes, orgsRes] = await Promise.all([
        fetch(`${apiBase}/api/v1/crm/pipeline`),
        fetch(`${apiBase}/api/v1/crm/opportunities`),
        fetch(`${apiBase}/api/v1/crm/activities`),
        fetch(`${apiBase}/api/v1/crm/contacts`),
        fetch(`${apiBase}/api/v1/people`),
        fetch(`${apiBase}/api/v1/people/organizations/list`),
      ]);

      if (pipeRes.ok) setPipelineData(await pipeRes.json());
      if (oppsRes.ok) setOpportunities(await oppsRes.json());
      if (actsRes.ok) setActivities(await actsRes.json());
      if (contactsRes.ok) setContacts(await contactsRes.json());
      if (peopleRes.ok) setPeople(await peopleRes.json());
      if (orgsRes.ok) setOrganizations(await orgsRes.json());
    } catch (e) {
      console.error("Failed to load CRM data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleStageChange = async (oppId: string, newStage: string) => {
    try {
      const res = await fetch(`${apiBase}/api/v1/crm/opportunities/${oppId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pipeline_stage: newStage }),
      });
      if (res.ok) {
        fetchData();
      }
    } catch (e) {
      console.error("Error moving opportunity stage:", e);
    }
  };

  const handleCreateDeal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...newDealForm,
        person_id: newDealForm.person_id || undefined,
        organization_id: newDealForm.organization_id || undefined,
        value: Number(newDealForm.value),
      };
      const res = await fetch(`${apiBase}/api/v1/crm/opportunities`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setShowNewDealModal(false);
        setNewDealForm({
          title: "",
          person_id: "",
          organization_id: "",
          value: 50000,
          currency: "ETB",
          pipeline_stage: "New Lead",
          probability: 20,
          expected_close_date: "",
          notes: "",
        });
        fetchData();
      }
    } catch (e) {
      console.error("Error creating deal:", e);
    }
  };

  const handleCreateActivity = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...newActForm,
        opportunity_id: newActForm.opportunity_id || undefined,
      };
      const res = await fetch(`${apiBase}/api/v1/crm/activities`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setShowNewActModal(false);
        setNewActForm({
          activity_type: "Call",
          subject: "",
          description: "",
          person_id: "",
          opportunity_id: "",
          due_date: "",
        });
        fetchData();
      }
    } catch (e) {
      console.error("Error logging activity:", e);
    }
  };

  const handleCompleteActivity = async (actId: string) => {
    try {
      const res = await fetch(`${apiBase}/api/v1/crm/activities/${actId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "Completed" }),
      });
      if (res.ok) {
        fetchData();
      }
    } catch (e) {
      console.error("Error updating activity:", e);
    }
  };

  const stagesList = ["New Lead", "Contacted", "Qualified", "Needs Analysis", "Proposal", "Negotiation", "Won", "Lost"];

  const filteredOpps = opportunities.filter((o) => {
    const s = search.toLowerCase();
    return !s || o.title?.toLowerCase().includes(s) || o.person_name?.toLowerCase().includes(s) || o.organization_name?.toLowerCase().includes(s);
  });

  const totalPipeVal = pipelineData?.total_pipeline_value || opportunities.filter((o) => o.status !== "Lost").reduce((a, b) => a + (b.value || 0), 0);
  const weightedVal = pipelineData?.weighted_pipeline_value || 0;
  const wonDealsCount = opportunities.filter((o) => o.pipeline_stage === "Won").length;

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-emerald-600/20 text-emerald-400 rounded-xl border border-emerald-500/30">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white tracking-tight">CRM & Sales Pipeline</h1>
            <p className="text-xs text-slate-400">Opportunity forecasting, multi-stage pipelines, deal values & activity scheduling.</p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setShowNewActModal(true)}
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition"
          >
            <Clock className="w-3.5 h-3.5 text-blue-400" />
            <span>Log Activity</span>
          </button>
          <button
            onClick={() => setShowNewDealModal(true)}
            className="px-4 py-2 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white rounded-xl text-xs font-bold shadow-lg shadow-red-600/20 flex items-center gap-1.5 transition"
          >
            <Plus className="w-4 h-4" />
            <span>New Opportunity</span>
          </button>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Total Pipeline Value</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-black text-emerald-400 mt-1">{totalPipeVal?.toLocaleString()} ETB</p>
          <p className="text-[11px] text-slate-400 mt-0.5">{opportunities.length} Total pipeline opportunities</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Weighted Forecast</span>
            <TrendingUp className="w-4 h-4 text-blue-400" />
          </div>
          <p className="text-2xl font-black text-blue-400 mt-1">{weightedVal?.toLocaleString()} ETB</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Probability-adjusted revenue</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Won Deals</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">{wonDealsCount}</p>
          <p className="text-[11px] text-emerald-400/80 mt-0.5">Successfully closed agreements</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Open Tasks & Activities</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">{activities.filter((a) => a.status === "Pending").length}</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Scheduled calls, meetings & follow-ups</p>
        </div>
      </div>

      {/* Tabs & Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-1.5 p-1 bg-slate-950 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab("pipeline")}
              className={`px-3.5 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                activeTab === "pipeline" ? "bg-red-600 text-white shadow-md" : "text-slate-400 hover:text-white"
              }`}
            >
              <TrendingUp className="w-3.5 h-3.5" />
              <span>Pipeline Kanban</span>
            </button>
            <button
              onClick={() => setActiveTab("opportunities")}
              className={`px-3.5 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                activeTab === "opportunities" ? "bg-red-600 text-white shadow-md" : "text-slate-400 hover:text-white"
              }`}
            >
              <Briefcase className="w-3.5 h-3.5" />
              <span>Deals List ({opportunities.length})</span>
            </button>
            <button
              onClick={() => setActiveTab("activities")}
              className={`px-3.5 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                activeTab === "activities" ? "bg-red-600 text-white shadow-md" : "text-slate-400 hover:text-white"
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>Activities ({activities.length})</span>
            </button>
            <button
              onClick={() => setActiveTab("contacts")}
              className={`px-3.5 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                activeTab === "contacts" ? "bg-red-600 text-white shadow-md" : "text-slate-400 hover:text-white"
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>CRM Directory</span>
            </button>
          </div>

          <div className="relative flex-1 sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search deals, contacts, companies..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-950 text-white text-xs pl-8 pr-3 py-2 rounded-xl border border-slate-800 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        {/* View 1: Pipeline Kanban */}
        {loading ? (
          <div className="py-16 text-center text-slate-400 text-xs animate-pulse">Loading CRM workspace...</div>
        ) : activeTab === "pipeline" ? (
          <div className="overflow-x-auto pb-4">
            <div className="flex gap-4 min-w-[1400px]">
              {stagesList.map((stage) => {
                const stageDeals = opportunities.filter((o) => o.pipeline_stage === stage);
                const stageSum = stageDeals.reduce((a, b) => a + (b.value || 0), 0);

                return (
                  <div key={stage} className="w-72 flex-shrink-0 bg-slate-950/70 border border-slate-800/90 rounded-2xl p-3 flex flex-col gap-3">
                    <div className="flex items-center justify-between border-b border-slate-800/80 pb-2 px-1">
                      <div>
                        <h4 className="text-xs font-bold text-white">{stage}</h4>
                        <span className="text-[10px] text-slate-400 font-medium">{stageDeals.length} deals · {stageSum.toLocaleString()} ETB</span>
                      </div>
                      <span
                        className={`w-2 h-2 rounded-full ${
                          stage === "Won" ? "bg-emerald-400" : stage === "Lost" ? "bg-red-500" : "bg-blue-400"
                        }`}
                      />
                    </div>

                    <div className="space-y-2.5 min-h-[300px]">
                      {stageDeals.map((deal) => (
                        <div
                          key={deal.id}
                          className="bg-slate-900 border border-slate-800 rounded-xl p-3 space-y-2.5 hover:border-slate-700 transition shadow-sm"
                        >
                          <div>
                            <p className="font-bold text-white text-xs leading-snug">{deal.title}</p>
                            <p className="text-[11px] text-slate-400 mt-0.5">
                              {deal.person_name || "Individual"} {deal.organization_name && `· ${deal.organization_name}`}
                            </p>
                          </div>

                          <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-800/60">
                            <span className="font-black text-emerald-400">{deal.value?.toLocaleString()} {deal.currency}</span>
                            <span className="text-[10px] font-bold text-slate-400">{deal.probability}% Prob</span>
                          </div>

                          {/* Quick Stage Progression */}
                          <div className="pt-1 flex items-center justify-between gap-1 text-[10px]">
                            <select
                              value={deal.pipeline_stage}
                              onChange={(e) => handleStageChange(deal.id, e.target.value)}
                              className="w-full bg-slate-950 text-slate-300 px-2 py-1 rounded-lg border border-slate-800 focus:outline-none"
                            >
                              {stagesList.map((s) => (
                                <option key={s} value={s}>{s}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : activeTab === "opportunities" ? (
          /* View 2: Opportunities Table */
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-3">Opportunity Title</th>
                  <th className="py-3 px-3">Contact / Org</th>
                  <th className="py-3 px-3">Deal Value</th>
                  <th className="py-3 px-3">Stage</th>
                  <th className="py-3 px-3">Probability</th>
                  <th className="py-3 px-3">Expected Close</th>
                  <th className="py-3 px-3 text-right">Move Stage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredOpps.map((opp) => (
                  <tr key={opp.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-3">
                      <div className="font-bold text-white text-sm">{opp.title}</div>
                      <div className="text-[11px] text-slate-400">Source: {opp.source || "Inquiry"}</div>
                    </td>
                    <td className="py-3.5 px-3 space-y-0.5">
                      <p className="font-medium text-slate-200">{opp.person_name || "—"}</p>
                      {opp.organization_name && <p className="text-slate-400 text-[11px]">{opp.organization_name}</p>}
                    </td>
                    <td className="py-3.5 px-3">
                      <span className="font-black text-emerald-400 text-sm">
                        {opp.value?.toLocaleString()} {opp.currency}
                      </span>
                    </td>
                    <td className="py-3.5 px-3">
                      <span className="px-2.5 py-1 rounded-md text-[11px] font-bold bg-slate-950 border border-slate-800 text-blue-400">
                        {opp.pipeline_stage}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 font-semibold text-slate-300">{opp.probability}%</td>
                    <td className="py-3.5 px-3 text-slate-400">{opp.expected_close_date || "—"}</td>
                    <td className="py-3.5 px-3 text-right">
                      <select
                        value={opp.pipeline_stage}
                        onChange={(e) => handleStageChange(opp.id, e.target.value)}
                        className="bg-slate-950 text-slate-200 text-xs px-2.5 py-1 rounded-lg border border-slate-800 focus:outline-none"
                      >
                        {stagesList.map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : activeTab === "activities" ? (
          /* View 3: Activities & Tasks */
          <div className="space-y-3">
            {activities.length === 0 ? (
              <div className="py-12 text-center text-slate-400 text-xs">No scheduled activities found.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {activities.map((act) => (
                  <div
                    key={act.id}
                    className={`bg-slate-950 border rounded-2xl p-4 space-y-2.5 transition ${
                      act.status === "Completed" ? "border-slate-800 opacity-60" : "border-slate-800 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="p-1.5 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 text-xs font-bold">
                          {act.activity_type}
                        </span>
                        <h4 className="font-bold text-white text-xs">{act.subject}</h4>
                      </div>
                      {act.status !== "Completed" ? (
                        <button
                          onClick={() => handleCompleteActivity(act.id)}
                          className="px-2.5 py-1 bg-emerald-600/20 hover:bg-emerald-600 text-emerald-400 hover:text-white rounded-lg text-[10px] font-bold transition flex items-center gap-1 border border-emerald-500/30"
                        >
                          <CheckCircle2 className="w-3 h-3" />
                          <span>Mark Done</span>
                        </button>
                      ) : (
                        <span className="text-[10px] font-bold text-emerald-400 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Completed
                        </span>
                      )}
                    </div>
                    {act.description && <p className="text-xs text-slate-300">{act.description}</p>}
                    <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
                      <span>Contact: <strong className="text-slate-200">{act.person_name || "—"}</strong></span>
                      <span className="flex items-center gap-1 text-slate-400">
                        <Clock className="w-3 h-3" />
                        {act.due_date ? new Date(act.due_date).toLocaleDateString() : "No deadline"}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          /* View 4: Contacts & Leads */
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-3">Contact Name</th>
                  <th className="py-3 px-3">Source Module</th>
                  <th className="py-3 px-3">Email & Phone</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Timeline Events</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {contacts.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-3 font-bold text-white">{c.full_name}</td>
                    <td className="py-3.5 px-3">
                      <span className="px-2 py-0.5 bg-slate-950 border border-slate-800 rounded text-slate-300 font-medium">
                        {c.source_module}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 space-y-0.5 text-slate-300">
                      <div>{c.email || "—"}</div>
                      <div className="text-[11px] text-slate-400">{c.phone || "—"}</div>
                    </td>
                    <td className="py-3.5 px-3">
                      <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded font-bold">
                        {c.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 text-slate-400 font-semibold">{c.timeline?.length || 0} events</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* New Deal Modal */}
      {showNewDealModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Create Sales Opportunity / Deal</h3>
              <button onClick={() => setShowNewDealModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleCreateDeal} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Opportunity Title *</label>
                <input
                  type="text"
                  required
                  value={newDealForm.title}
                  onChange={(e) => setNewDealForm({ ...newDealForm, title: e.target.value })}
                  placeholder="e.g. Enterprise ERP Automation Project"
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Associated Person</label>
                  <select
                    value={newDealForm.person_id}
                    onChange={(e) => setNewDealForm({ ...newDealForm, person_id: e.target.value })}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  >
                    <option value="">Select Person</option>
                    {people.map((p) => (
                      <option key={p.id} value={p.id}>{p.full_name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Organization</label>
                  <select
                    value={newDealForm.organization_id}
                    onChange={(e) => setNewDealForm({ ...newDealForm, organization_id: e.target.value })}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  >
                    <option value="">Select Organization</option>
                    {organizations.map((o) => (
                      <option key={o.id} value={o.id}>{o.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Deal Value (ETB) *</label>
                  <input
                    type="number"
                    required
                    value={newDealForm.value}
                    onChange={(e) => setNewDealForm({ ...newDealForm, value: Number(e.target.value) })}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Initial Stage</label>
                  <select
                    value={newDealForm.pipeline_stage}
                    onChange={(e) => setNewDealForm({ ...newDealForm, pipeline_stage: e.target.value })}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  >
                    {stagesList.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Notes & Scope</label>
                <textarea
                  rows={2}
                  value={newDealForm.notes}
                  onChange={(e) => setNewDealForm({ ...newDealForm, notes: e.target.value })}
                  placeholder="Key deliverables, timeline expectations, decision makers..."
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowNewDealModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl"
                >
                  Create Opportunity
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Activity Modal */}
      {showNewActModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Log CRM Activity / Task</h3>
              <button onClick={() => setShowNewActModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleCreateActivity} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Activity Type</label>
                  <select
                    value={newActForm.activity_type}
                    onChange={(e) => setNewActForm({ ...newActForm, activity_type: e.target.value })}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  >
                    <option value="Call">Call</option>
                    <option value="Email">Email</option>
                    <option value="Meeting">Meeting</option>
                    <option value="SMS">SMS</option>
                    <option value="WhatsApp">WhatsApp</option>
                    <option value="Task">Task</option>
                    <option value="Follow-up">Follow-up</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Target Contact *</label>
                  <select
                    required
                    value={newActForm.person_id}
                    onChange={(e) => setNewActForm({ ...newActForm, person_id: e.target.value })}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  >
                    <option value="">Select Contact</option>
                    {people.map((p) => (
                      <option key={p.id} value={p.id}>{p.full_name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Subject *</label>
                <input
                  type="text"
                  required
                  value={newActForm.subject}
                  onChange={(e) => setNewActForm({ ...newActForm, subject: e.target.value })}
                  placeholder="e.g. Discuss Next.js and API architecture requirements"
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Details & Meeting Notes</label>
                <textarea
                  rows={2}
                  value={newActForm.description}
                  onChange={(e) => setNewActForm({ ...newActForm, description: e.target.value })}
                  placeholder="Action items, takeaways, customer feedback..."
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowNewActModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl"
                >
                  Save Activity
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
